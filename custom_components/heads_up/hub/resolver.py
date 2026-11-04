"""Resolver: turns an audience or a recipient list into recipients, with reasons.

Used by the engine, the dry run and the panel preview, so what is previewed is what is delivered
(DESIGN §23.7). Membership is a snapshot taken when called. Reason codes are stable strings the
trace and the panel translate.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant

from ..const import (
    BANNER_NOBODY,
    CHANNEL_MAIL,
    GROUP_SUFFIX,
    MAIL_GLOBAL,
    MAIL_GLOBAL_KEY,
    OPT_AUDIENCES_DISABLED,
    OPT_MAIL_ADDRESS,
    OPT_PRESENCE_DEBOUNCE,
    ZONE_KINDS,
)
from .audiences import BUILTINS, Audience, parse_audience
from .presence import PresenceTracker, is_unknown
from .recipients import (
    Group,
    Profile,
    StoredProfile,
    area_ids,
    area_speakers,
    build_profile,
    find_area,
    notify_service,
    parse_group,
    parse_profile,
    registrations,
    speaker_entities,
    unique,
)


@dataclass(frozen=True, slots=True)
class Recipient:
    key: str  # ledger key: person, `device:<id>` or an entity id
    kind: str  # person, device, speaker
    person: str | None = None
    service: str | None = None  # notify service of a device, worked out now (N-78)
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class Skipped:
    who: str
    reason: str


@dataclass(slots=True)
class Resolution:
    recipients: list[Recipient] = field(default_factory=list)
    skipped: list[Skipped] = field(default_factory=list)


class HubResolver:
    def __init__(self, hass: HomeAssistant, options: Mapping[str, Any]) -> None:
        self._hass = hass
        self._options = options
        self.presence = PresenceTracker(hass, lambda: int(options[OPT_PRESENCE_DEBOUNCE]))
        self._audiences: dict[str, Audience] = {}
        self._groups: dict[str, Group] = {}
        self._profiles: dict[str, StoredProfile] = {}

    async def async_start(self) -> None:
        await self.presence.async_start()

    async def async_stop(self) -> None:
        await self.presence.async_stop()

    def sync(self, subentries: Mapping[str, ConfigSubentry]) -> None:
        """Read the audience, group and profile subentries (beside `sync_rules`)."""
        audiences = (parse_audience(s) for s in subentries.values())
        self._audiences = {a.name: a for a in audiences if a is not None}
        groups = (parse_group(s) for s in subentries.values())
        self._groups = {g.name: g for g in groups if g is not None}
        profiles = (parse_profile(s) for s in subentries.values())
        self._profiles = {p.person: p for p in profiles if p is not None}

    # Names a call may use ---------------------------------------------------------------

    def names(self) -> list[str]:
        """Audience names (implements the H1 interface)."""
        return [*(n for n in BUILTINS if n not in self.disabled_audiences()), *self._audiences]

    def known(self, channel: str) -> list[str]:
        """Recipients a channel accepts (implements the H1 interface)."""
        persons = sorted(s.entity_id for s in self._hass.states.async_all("person"))
        if channel == "speak":
            groups = [f"{n}{GROUP_SUFFIX}" for n in self._groups]
            return [*speaker_entities(self._hass), *groups, *area_ids(self._hass)]
        if channel == "push":
            return [*persons, *registrations(self._hass)]
        if channel == CHANNEL_MAIL:
            return [*persons, MAIL_GLOBAL]
        return persons

    def accepts(self, channel: str, name: str) -> bool:
        """Whether a call may name this recipient. Speech also takes an area by its name."""
        if name in self.known(channel):
            return True
        return channel == "speak" and find_area(self._hass, name) is not None

    def groups(self) -> list[Group]:
        return list(self._groups.values())

    def disabled_audiences(self) -> set[str]:
        """Built-in audiences the admin switched off (D-136): not offered, refused in calls."""
        return set(self._options.get(OPT_AUDIENCES_DISABLED, []))

    def audience(self, name: str) -> Audience | None:
        if name in BUILTINS and name not in self.disabled_audiences():
            return BUILTINS[name]
        return self._audiences.get(name)

    def persons_of_user(self, user_id: str) -> list[str]:
        """Persons linked to a Home Assistant user (N-10)."""
        return [
            s.entity_id
            for s in self._hass.states.async_all("person")
            if s.attributes.get("user_id") == user_id
        ]

    def user_of_person(self, person: str) -> str | None:
        state = self._hass.states.get(person)
        user_id = state.attributes.get("user_id") if state else None
        return str(user_id) if user_id else None

    def profile(self, person: str) -> Profile:
        return build_profile(self._hass, person, self._profiles.get(person))

    # Resolution -------------------------------------------------------------------------

    async def members(self, audience: Audience, severity: str) -> Resolution:
        """The persons of an audience right now, with the reason for each."""
        result = Resolution()
        persons = sorted(s.entity_id for s in self._hass.states.async_all("person"))
        kind = audience.kind
        if kind == "persons":
            for person in audience.persons:
                if self._hass.states.get(person) is None:
                    result.skipped.append(Skipped(person, "person_not_found"))
                else:
                    result.recipients.append(Recipient(person, "person", person, reason="listed"))
        elif kind == "everyone":
            result.recipients = [Recipient(p, "person", p, reason="everyone") for p in persons]
        elif kind == "admins":
            for person in persons:
                user_id = self._hass.states.get(person).attributes.get("user_id")  # type: ignore[union-attr]
                user = await self._hass.auth.async_get_user(user_id) if user_id else None
                # A person without a Home Assistant user is not an administrator: not a member,
                # and not listed as skipped either.
                if user is not None and user.is_admin:
                    result.recipients.append(Recipient(person, "person", person, reason="admin"))
        elif kind in ("last_to_leave", "first_home"):
            person = getattr(self.presence, kind)
            if (
                person
                and self._hass.states.get(person) is not None
                and (not audience.limit or person in audience.limit)
            ):
                result.recipients.append(Recipient(person, "person", person, reason=kind))
        else:
            for person in persons:
                if audience.limit and person not in audience.limit:
                    continue
                self._presence_member(result, person, kind, audience.zone, severity)
        return self._without_disabled(result)

    def _without_disabled(self, result: Resolution) -> Resolution:
        """A disabled recipient is in no audience: the member becomes a skip (D-147)."""
        kept: list[Recipient] = []
        for member in result.recipients:
            if self.profile(member.key).enabled:
                kept.append(member)
            else:
                result.skipped.append(Skipped(member.key, "recipient_disabled"))
        result.recipients = kept
        return result

    def enabled_people(self, people: list[str]) -> list[str]:
        """The persons of a banner call that are not disabled; a banner for persons who are all
        disabled is shown to nobody, not to everyone."""
        kept = [p for p in people if self.profile(p).enabled]
        return kept or ([BANNER_NOBODY] if people else [])

    def _presence_member(
        self, result: Resolution, person: str, kind: str, zone: str | None, severity: str
    ) -> None:
        state = self._hass.states.get(person)
        if is_unknown(state):
            # Unknown presence: critical notifies anyway, lower severities skip (D-080).
            if severity == "critical":
                result.recipients.append(
                    Recipient(person, "person", person, reason="presence_unknown_critical")
                )
            else:
                result.skipped.append(Skipped(person, "presence_unknown"))
            return
        assert state is not None
        if kind in ZONE_KINDS:
            zones = state.attributes.get("in_zones") or []
            inside = bool(zone) and (zone in zones or state.state == str(zone).split(".", 1)[-1])
            match = inside if kind == "in_zone" else not inside
        else:
            match = (state.state == "home") == (kind == "at_home")
        if match:
            result.recipients.append(
                Recipient(person, "person", person, reason=f"state:{state.state}")
            )

    async def banner_people(self, name: str, severity: str) -> list[str]:
        """The `people` of a banner that names an audience, as of now (D-131). Everyone limits
        nothing; an audience that is empty now gives a banner nobody sees."""
        audience = self.audience(name)
        if audience is None or audience.kind == "everyone":
            return []
        members = await self.members(audience, severity)
        return [r.key for r in members.recipients] or [BANNER_NOBODY]

    async def resolve(
        self, target: Mapping[str, Any] | None, channel: str, severity: str
    ) -> Resolution:
        """Recipients of one channel for a call's target. Persistent and banner need none."""
        target = target or {}
        out = Resolution()
        if channel == "speak":
            self._speakers(out, target.get("recipients", []))
            return out
        persons: list[str] = []
        if "audience" in target:
            audience = self.audience(target["audience"])
            if audience is None:
                out.skipped.append(Skipped(str(target["audience"]), "unknown_audience"))
                return out
            members = await self.members(audience, severity)
            out.skipped += members.skipped
            persons = [r.key for r in members.recipients]
        else:
            direct = list(target.get("recipients", []))
            persons = [p for p in direct if p.startswith("person.")]
            if channel == "push":
                names = registrations(self._hass)
                for item in direct:
                    if item in names:
                        out.recipients.append(self._device_recipient(None, item, names))
            elif channel == CHANNEL_MAIL:
                if MAIL_GLOBAL in direct:
                    self._global_address(out)
                out.skipped += [
                    Skipped(p, "unknown_recipient")
                    for p in direct
                    if p not in persons and p != MAIL_GLOBAL
                ]
            elif any(not p.startswith("person.") for p in direct):
                out.skipped += [Skipped(p, "unknown_recipient") for p in direct if p not in persons]
        for person in unique(persons):
            self._expand_person(out, person, channel)
        return out

    def _global_address(self, out: Resolution) -> None:
        if str(self._options.get(OPT_MAIL_ADDRESS) or "").strip():
            out.recipients.append(Recipient(MAIL_GLOBAL_KEY, "address"))
        else:
            out.skipped.append(Skipped(MAIL_GLOBAL, "no_mail_address"))

    def _expand_person(self, out: Resolution, person: str, channel: str) -> None:
        profile = self.profile(person)
        if not profile.enabled:
            out.skipped.append(Skipped(person, "recipient_disabled"))
        elif channel not in profile.channels:
            out.skipped.append(Skipped(person, "channel_not_accepted"))
        elif channel == CHANNEL_MAIL and not profile.mail_address:
            out.skipped.append(Skipped(person, "no_mail_address"))
        elif channel != "push":
            out.recipients.append(Recipient(person, "person", person))
        elif not profile.devices:
            out.skipped.append(Skipped(person, "no_usable_device"))
        else:
            names = registrations(self._hass)
            for device in profile.devices:
                if device.service_found:
                    out.recipients.append(self._device_recipient(person, device.device_id, names))
                else:
                    reason = "service_not_found" if device.name else "device_missing"
                    out.skipped.append(Skipped(f"device:{device.device_id}", reason))
            if not any(r.person == person for r in out.recipients):
                out.skipped.append(Skipped(person, "no_usable_device"))

    def _device_recipient(
        self, person: str | None, device_id: str, names: Mapping[str, str]
    ) -> Recipient:
        name = names.get(device_id)
        return Recipient(
            f"device:{device_id}",
            "device",
            person,
            notify_service(name) if name else None,
        )

    def _speakers(self, out: Resolution, requested: list[str]) -> None:
        speakers = set(speaker_entities(self._hass))
        for item in requested:
            if item in speakers:
                out.recipients.append(Recipient(item, "speaker"))
                continue
            group = (
                self._groups.get(item.removesuffix(GROUP_SUFFIX))
                if item.endswith(GROUP_SUFFIX)
                else None
            )
            if group is not None:
                members = [*group.members]
                for area in group.areas:
                    members += area_speakers(self._hass, area)
                found = [m for m in unique(members) if m in speakers]
                if not found:
                    out.skipped.append(Skipped(item, "group_empty"))
                out.recipients += [
                    Recipient(m, "speaker", reason=f"group:{group.name}") for m in found
                ]
            elif (found_area := find_area(self._hass, item)) is not None:
                found = [m for m in area_speakers(self._hass, found_area) if m in speakers]
                if not found:
                    out.skipped.append(Skipped(item, "group_empty"))
                out.recipients += [
                    Recipient(m, "speaker", reason=f"area:{found_area}") for m in found
                ]
            else:
                out.skipped.append(Skipped(item, "unknown_recipient"))
        by_key = {r.key: r for r in reversed(out.recipients)}  # one delivery per speaker
        out.recipients = [by_key[k] for k in dict.fromkeys(r.key for r in out.recipients)]
