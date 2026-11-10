"""Put back the data of Heads Up from before the move to keys (D-200).

Run it with Home Assistant stopped, on the configuration directory, before installing an earlier
release. It reads `.storage/heads_up.migration_v2` (written once, before the first change) and
restores the Heads Up config entry (version, options, subentries) and the banner, delivery and
trace stores to the state the backup holds. Everything else in `core.config_entries` stays.

    python scripts/restore_identity_backup.py /path/to/config [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DOMAIN = "heads_up"
BACKUP = "heads_up.migration_v2"
# The stores as version 1 wrote them: file name to (version, minor version).
STORES = {"heads_up.banners": (1, 1), "heads_up.deliveries": (1, 1), "heads_up.trace": (1, 1)}


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def restore(config_dir: Path, dry_run: bool = False) -> list[str]:
    """Returns what was (or would be) done, one line each. Raises FileNotFoundError when there is
    no backup and ValueError when the entry is not found."""
    storage = config_dir / ".storage"
    backup = _read(storage / BACKUP)["data"]
    entries = _read(storage / "core.config_entries")
    found = [e for e in entries["data"]["entries"] if e["domain"] == DOMAIN]
    if not found:
        raise ValueError("no Heads Up config entry in core.config_entries")
    done = []
    old = backup["entry"]
    entry = found[0]
    entry["version"] = old["version"]
    entry["options"] = old["options"]
    entry["subentries"] = [
        {
            "data": s["data"],
            "subentry_id": s["subentry_id"],
            "subentry_type": s["subentry_type"],
            "title": s["title"],
            "unique_id": s["unique_id"],
        }
        for s in old["subentries"]
    ]
    done.append(f"config entry: version {old['version']}, {len(old['subentries'])} subentries")
    if not dry_run:
        _write(storage / "core.config_entries", entries)
    for key, (version, minor) in STORES.items():
        data = backup["stores"].get(key)
        if data is None:
            done.append(f"{key}: not in the backup, left as it is")
            continue
        done.append(f"{key}: restored")
        if not dry_run:
            _write(
                storage / key,
                {"version": version, "minor_version": minor, "key": key, "data": data},
            )
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
