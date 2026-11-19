"""Put back the Away policies of Heads Up from before they became Presence (D-214).

Run it with Home Assistant stopped, on the configuration directory, before installing 1.0.0
again. It reads `.storage/heads_up.migration_v2_2` (written once, before the conversion) and
puts back the data of the policy subentries it holds, and the minor version 1 of the Heads Up
config entry. Other subentries, the options and every other config entry stay as they are.

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


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    if not dry_run:
        _write(storage / "core.config_entries", entries)
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
