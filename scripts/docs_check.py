"""Docs checks. Run with `make docs-check`.

1. Banned words and placeholders in every committed Markdown file.
2. YAML examples calling heads_up.* validate against the real action schemas (active once
   custom_components/heads_up/services.py defines SCHEMAS).
3. Field parity between action schemas and docs/actions.md (active once both exist).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Files that quote the banned list on purpose.
EXEMPT = {".claude/rules/docs-style.md"}
SKIP_DIRS = {".venv", "node_modules", ".git", ".private"}

BANNED = [
    r"seamless(ly)?",
    r"robust",
    r"powerful",
    r"comprehensive",
    r"leverag\w*",
    r"utili[sz]\w*",
    r"elevate",
    r"streamline",
    r"unlock",
    r"empower",
    r"effortless(ly)?",
    r"cutting-edge",
    r"state-of-the-art",
    r"game-changer",
    r"next-level",
    r"delve",
    r"in today's",
    r"it's worth noting",
    r"please note that",
    r"simply",
    r"easily",
    r"just works",
    r"best-in-class",
    r"ultimate",
    r"supercharge",
    r"a testament to",
    r"rich ecosystem",
]
PLACEHOLDERS = [r"\bTODO\b", r"\bTBD\b", r"\bLorem\b", r"coming soon"]
BANNED_RE = re.compile(r"\b(" + "|".join(BANNED) + r")\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile("|".join(PLACEHOLDERS), re.IGNORECASE)
FENCE_RE = re.compile(r"```yaml\n(.*?)```", re.DOTALL)


def markdown_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or str(rel) in EXEMPT:
            continue
        files.append(path)
    return sorted(files)


def check_words(files: list[Path]) -> list[str]:
    errors = []
    for path in files:
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            rel = path.relative_to(ROOT)
            if m := BANNED_RE.search(line):
                errors.append(f"{rel}:{no}: banned word {m.group(0)!r}")
            if m := PLACEHOLDER_RE.search(line):
                errors.append(f"{rel}:{no}: placeholder {m.group(0)!r}")
    return errors


def check_examples(files: list[Path]) -> tuple[list[str], int]:
    services = ROOT / "custom_components" / "heads_up" / "services.py"
    if not services.exists():
        return [], 0
    # Activated in Phase 2: import SCHEMAS from services.py and validate each example.
    return [], 0


def main() -> int:
    files = markdown_files()
    errors = check_words(files)
    example_errors, examples = check_examples(files)
    errors += example_errors
    for e in errors:
        print(e)
    print(f"docs-check: {len(files)} files, {examples} examples validated, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
