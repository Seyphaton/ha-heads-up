"""Put back the Away policies of Heads Up from before they became Presence (D-214).

Run it with Home Assistant stopped, on the configuration directory, before installing 1.0.0
again. It reads `.storage/heads_up.migration_v2_2` (written once, before the conversion) and
puts back the data of the policy subentries it holds, and the minor version 1 of the Heads Up
config entry. It also names the severity `passive` `success` again (D-231), in the options, the
subentries and the stored messages, because 1.0.0 does not know `passive`. Every other config
entry stays as it is.

    python scripts/restore_presence_backup.py /path/to/config [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DOMAIN = "heads_up"
BACKUP = "heads_up.migration_v2_2"
# The stores that hold a message's severity; 1.0.0 reads all three.
STORES = ("heads_up.banners", "heads_up.deliveries", "heads_up.trace")
# Options keyed by severity (hub/migration.py SEVERITY_KEYED_OPTIONS).
SEVERITY_KEYED = ("push_levels", "popup_styles", "severity_display", "speak_severity_volume")


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def severity_back(value: Any) -> Any:
    """`passive` back to `success` where it is a severity: the value of `severity`, an item of
    `severities`, and a key of the options keyed by severity. A push level `passive` stays."""
    if isinstance(value, list):
        return [severity_back(item) for item in value]
    if not isinstance(value, dict):
        return value
    out: dict[str, Any] = {}
    for key, item in value.items():
        if key == "severity" and item == "passive":
            item = "success"
        elif key == "severities" and isinstance(item, list):
            item = ["success" if s == "passive" else s for s in item]
        elif key in SEVERITY_KEYED and isinstance(item, dict):
            item = {("success" if k == "passive" else k): v for k, v in item.items()}
        else:
            item = severity_back(item)
        out[key] = item
    return out


def restore(config_dir: Path, dry_run: bool = False) -> list[str]:
    """Returns what was (or would be) done, one line each. Raises FileNotFoundError when there is
    no backup and ValueError when the entry is not found."""
    storage = config_dir / ".storage"
    backup = _read(storage / BACKUP)["data"]["entry"]
    entries = _read(storage / "core.config_entries")
    found = [e for e in entries["data"]["entries"] if e["domain"] == DOMAIN]
    if not found:
        raise ValueError("no Heads Up config entry in core.config_entries")
    entry = found[0]
    old = {s["subentry_id"]: s for s in backup["subentries"]}
    done = []
    for sub in entry.get("subentries", []):
        if (before := old.get(sub["subentry_id"])) is not None and sub["data"] != before["data"]:
            sub["data"] = before["data"]
            done.append(f"policy {sub['title']}: put back")
    entry["minor_version"] = backup.get("minor_version", 1)
    done.append(f"config entry: minor version {entry['minor_version']}")
    if (options := severity_back(entry.get("options", {}))) != entry.get("options", {}):
        entry["options"] = options
        done.append("options: passive named success again")
    for sub in entry.get("subentries", []):
        if (data := severity_back(sub["data"])) != sub["data"]:
            sub["data"] = data
            kind = sub.get("subentry_type", "subentry")
            done.append(f"{kind} {sub['title']}: passive named success again")
    stores = {}
    for key in STORES:
        if (path := storage / key).exists():
            stored = _read(path)
            if (renamed := severity_back(stored)) != stored:
                stores[path] = renamed
                done.append(f"{key}: passive named success again")
    if not dry_run:
        _write(storage / "core.config_entries", entries)
        for path, data in stores.items():
            _write(path, data)
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("config_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        for line in restore(args.config_dir, args.dry_run):
            print(line)
    except (FileNotFoundError, ValueError) as err:
        print(f"Nothing restored: {err}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("Dry run: nothing was written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
