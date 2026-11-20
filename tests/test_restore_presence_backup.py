"""The Presence rollback script puts the Away policies back as the backup holds them (D-214)."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import restore_presence_backup as restore


def write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def make(tmp_path: Path) -> Path:
    storage = tmp_path / ".storage"
    storage.mkdir()
    away = {"subentry_id": "P1", "subentry_type": "policy", "title": "Away", "unique_id": None}
    write(
        storage / "heads_up.migration_v2_2",
        {
            "version": 1,
            "data": {
                "entry": {
                    "version": 2,
                    "minor_version": 1,
                    "subentries": [{**away, "data": {"type": "away", "max_wait": 30}}],
                }
            },
        },
    )
    rule = {"subentry_id": "R1", "subentry_type": "rule", "title": "Door", "unique_id": None}
    write(
        storage / "core.config_entries",
        {
            "version": 1,
            "data": {
                "entries": [
                    {"domain": "other", "minor_version": 3, "subentries": []},
                    {
                        "domain": "heads_up",
                        "version": 2,
                        "minor_version": 2,
                        "subentries": [
                            {
                                **away,
                                "data": {"type": "presence", "max_wait": 30, "after_wait": "drop"},
                            },
                            {**rule, "data": {"entity_id": "binary_sensor.door"}},
                        ],
                    },
                ]
            },
        },
    )
    return tmp_path


def test_puts_back_the_away_policy_and_the_minor_version(tmp_path: Path) -> None:
    config = make(tmp_path)
    lines = restore.restore(config)
    entries = json.loads((config / ".storage" / "core.config_entries").read_text())["data"][
        "entries"
    ]
    other, mine = entries
    assert other == {"domain": "other", "minor_version": 3, "subentries": []}
    assert mine["minor_version"] == 1
    assert mine["subentries"][0]["data"] == {"type": "away", "max_wait": 30}
    assert mine["subentries"][1]["data"] == {"entity_id": "binary_sensor.door"}
    assert lines == ["policy Away: put back", "config entry: minor version 1"]


def test_a_dry_run_writes_nothing(tmp_path: Path) -> None:
    config = make(tmp_path)
    before = (config / ".storage" / "core.config_entries").read_text()
    restore.restore(config, dry_run=True)
    assert (config / ".storage" / "core.config_entries").read_text() == before


def test_without_a_backup_nothing_happens(tmp_path: Path) -> None:
    (tmp_path / ".storage").mkdir()
    with pytest.raises(FileNotFoundError):
        restore.restore(tmp_path)


def test_names_the_severity_passive_success_again_for_1_0(tmp_path: Path) -> None:
    config = make(tmp_path)
    path = config / ".storage" / "core.config_entries"
    entries = json.loads(path.read_text())
    mine = entries["data"]["entries"][1]
    mine["options"] = {"push_levels": {"passive": "passive", "info": "passive"}, "x": "passive"}
    mine["subentries"][1]["data"] = {"entity_id": "binary_sensor.door", "severity": "passive"}
    path.write_text(json.dumps(entries))
    banners = {"version": 3, "data": {"banners": {"b": {"id": "b", "severity": "passive"}}}}
    write(config / ".storage" / "heads_up.banners", banners)
    lines = restore.restore(config)
    mine = json.loads(path.read_text())["data"]["entries"][1]
    assert mine["options"] == {
        "push_levels": {"success": "passive", "info": "passive"},
        "x": "passive",
    }
    assert mine["subentries"][1]["data"]["severity"] == "success"
    stored = json.loads((config / ".storage" / "heads_up.banners").read_text())
    assert stored["data"]["banners"]["b"]["severity"] == "success"
    assert lines[2:] == [
        "options: passive named success again",
        "rule Door: passive named success again",
        "heads_up.banners: passive named success again",
    ]


def test_a_policy_list_of_severities_is_renamed_too() -> None:
    assert restore.severity_back({"severities": ["passive", "info"]}) == {
        "severities": ["success", "info"]
    }
