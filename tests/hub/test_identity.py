"""References are keys, not names (D-199): the lookups are pure and run twice without a change."""

from homeassistant.config_entries import ConfigSubentry

from custom_components.heads_up.hub.identity import IdentityMaps


def subentries() -> list[ConfigSubentry]:
    def sub(kind: str, title: str, sid: str) -> ConfigSubentry:
        return ConfigSubentry(
            data={}, subentry_type=kind, title=title, unique_id=None, subentry_id=sid
        )

    return [
        sub("policy", "Water", "P1"),
        sub("audience", "Parents", "A1"),
        sub("recipient_group", "Ground floor", "G1"),
    ]


def maps() -> IdentityMaps:
    return IdentityMaps.from_subentries(subentries(), {"kitchen": "Kitchen"})


def test_a_policy_name_a_timer_key_and_an_id_all_mean_the_same_policy() -> None:
    found = maps()
    assert found.policy("Water") == "P1"
    assert found.policy("water") == "P1"
    assert found.policy("escalation:Water") == "P1"
    assert found.policy("P1") == "P1"


def test_the_keywords_and_unknown_names_are_kept() -> None:
    found = maps()
    assert found.policy("none") == "none" and found.policy("automatic") == "automatic"
    assert found.policy("Gone") == "name:Gone"
    assert found.policy("name:Gone") == "name:Gone"
    # A dangling name resolves again when a policy with that title exists.
    later = IdentityMaps.from_subentries(
        [
            *subentries(),
            ConfigSubentry(
                data={}, subentry_type="policy", title="Gone", unique_id=None, subentry_id="P2"
            ),
        ]
    )
    assert later.policy("name:Gone") == "P2"


def test_audiences_use_the_kind_or_the_subentry_id() -> None:
    found = maps()
    assert found.audience("At home") == "at_home"
    assert found.audience("at_home") == "at_home"
    assert found.audience("parents") == "A1"
    assert found.audience("Nobody") == "name:Nobody"


def test_a_group_and_an_area_become_tokens() -> None:
    found = maps()
    assert found.recipient("Ground floor (group)") == "group:G1"
    assert found.recipient("kitchen") == "area:kitchen"
    assert found.recipient("Kitchen") == "area:kitchen"
    assert found.recipient("media_player.hall") == "media_player.hall"
    assert found.recipient("device:abc") == "device:abc"
    assert found.recipient("Unknown (group)") == "Unknown (group)"


def test_every_conversion_is_idempotent() -> None:
    found = maps()
    banner = {
        "policy": ["automatic", "Water"],
        "targets": {
            "push": {"audience": "Parents"},
            "speak": {"recipients": ["Ground floor (group)", "Kitchen"]},
        },
    }
    once = found.banner(banner)
    assert once == {
        "policy": ["automatic", "P1"],
        "targets": {
            "push": {"audience": "A1"},
            "speak": {"recipients": ["group:G1", "area:kitchen"]},
        },
    }
    assert found.banner(once) == once
    row = {
        "channel": "timer",
        "recipient": "escalation:Water",
        "message_id": "summary:summarize:Water",
    }
    migrated = found.timer_row(row)
    assert migrated["recipient"] == "P1" and migrated["message_id"] == "summary:P1"
    assert found.timer_row(migrated) == migrated
    held = {"policy": "summarize:Water", "targets": {"push": {"audience": "At home"}}}
    assert (
        found.held(found.held(held))
        == found.held(held)
        == {
            "policy": "P1",
            "targets": {"push": {"audience": "at_home"}},
        }
    )
