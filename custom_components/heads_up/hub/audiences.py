"""Audience definitions: built in and custom (DESIGN §23.7, D-080, D-088)."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigSubentry

from ..const import AUDIENCE_SUBENTRY, BUILTIN_AUDIENCES


@dataclass(frozen=True, slots=True)
class Audience:
    name: str
    # everyone, admins, persons, or a presence kind (at_home, not_home, last_to_leave,
    # first_home, in_zone, not_in_zone).
    kind: str
    builtin: bool = False
    persons: tuple[str, ...] = ()
    zone: str | None = None
    # Presence audiences only: the persons the audience is limited to; empty means every person.
    limit: tuple[str, ...] = ()
    # What a stored reference holds: the kind of a built-in audience, the subentry ID of a custom
    # one. The name is for display (D-199).
    key: str = ""


BUILTINS: dict[str, Audience] = {
    name: Audience(name, kind, builtin=True, key=kind) for name, kind in BUILTIN_AUDIENCES.items()
}


def parse_audience(subentry: ConfigSubentry) -> Audience | None:
    if subentry.subentry_type != AUDIENCE_SUBENTRY:
        return None
    data = subentry.data
    if data.get("kind") == "persons":
        return Audience(
            subentry.title,
            "persons",
            persons=tuple(data.get("persons", ())),
            key=subentry.subentry_id,
        )
    if data.get("presence"):
        return Audience(
            subentry.title,
            str(data["presence"]),
            zone=data.get("zone"),
            limit=tuple(data.get("limit", ())),
            key=subentry.subentry_id,
        )
    return None
