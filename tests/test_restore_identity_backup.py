"""The rollback script puts the entry and the stores back as the backup holds them (D-200)."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import restore_identity_backup as restore


def write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def make(tmp_path: Path) -> Path:
    storage = tmp_path / ".storage"
    storage.mkdir()
    old_sub = {
        "subentry_id": "S1",
        "subentry_type": "rule",
        "title": "Window",
        "unique_id": None,
        "data": {"policy": "Night"},
    }
    write(
        storage / "heads_up.migration_v2",
        {
            "version": 1,
            "data": {
                "entry": {"version": 1, "options": {"policy_mode": "all"}, "subentries": [old_sub]},
                "stores": {
                    "heads_up.banners": {"banners": [{"id": "m", "policy": ["Night"]}]},
                    "heads_up.deliveries": {"deliveries": [], "held": []},
                    "heads_up.trace": None,
                },
            },
        },
    )
    write(
        storage / "core.config_entries",
        {
            "version": 1,
            "data": {
                "entries": [
                    {"domain": "other", "version": 5, "options": {"keep": True}, "subentries": []},
                    {
                        "domain": "heads_up",
                        "version": 2,
                        "options": {"policy_mode": "all"},
                        "subentries": [{**old_sub, "data": {"policy": "KEY1"}}],
                    },
                ]
            },
        },
    )
    write(storage / "heads_up.banners", {"version": 2, "data": {"banners": []}})
    return tmp_path


def test_it_restores_the_entry_and_the_stores_and_leaves_other_entries(tmp_path: Path) -> None:
    config = make(tmp_path)
    done = restore.restore(config)
    entries = json.loads((config / ".storage" / "core.config_entries").read_text())["data"][
        "entries"
    ]
    other, ours = entries
    assert other == {"domain": "other", "version": 5, "options": {"keep": True}, "subentries": []}
    assert ours["version"] == 1 and ours["subentries"][0]["data"] == {"policy": "Night"}
    banners = json.loads((config / ".storage" / "heads_up.banners").read_text())
    assert banners["version"] == 1 and banners["data"]["banners"][0]["policy"] == ["Night"]
    assert any("heads_up.trace: not in the backup" in line for line in done)


def test_a_dry_run_writes_nothing(tmp_path: Path) -> None:
    config = make(tmp_path)
    before = (config / ".storage" / "core.config_entries").read_text()
    restore.restore(config, dry_run=True)
    assert (config / ".storage" / "core.config_entries").read_text() == before


def test_without_a_backup_it_stops(tmp_path: Path) -> None:
    (tmp_path / ".storage").mkdir()
    with pytest.raises(FileNotFoundError):
        restore.restore(tmp_path)
