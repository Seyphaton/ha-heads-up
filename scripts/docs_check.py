"""Docs checks. Run with `make docs-check`.

1. Banned words and placeholders in every committed Markdown file.
2. YAML examples in user docs that call heads_up.* validate against the real action schemas.
3. Field parity: action schema == services.yaml fields == docs/actions.md field tables.
4. Card option parity: CONFIG_KEYS in the card module == docs/card.md options table; card YAML
   examples use only those options.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

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


def human_docs(files: list[Path]) -> list[Path]:
    """README and user pages; design/dev docs may show planned fields and are not checked."""
    internal = {"DESIGN.md", "DECISIONS.md", "OPEN_QUESTIONS.md"}
    return [
        p
        for p in files
        if p == ROOT / "README.md" or (p.parent == ROOT / "docs" and p.name not in internal)
    ]


def _action_calls(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, list):
        return [c for item in node for c in _action_calls(item)]
    if isinstance(node, dict):
        calls = [node] if str(node.get("action", "")).startswith("heads_up.") else []
        return calls + [c for v in node.values() for c in _action_calls(v)]
    return []


def check_examples(files: list[Path]) -> tuple[list[str], int]:
    import voluptuous as vol
    import yaml

    from custom_components.heads_up.services import SCHEMAS

    errors, count = [], 0
    for path in human_docs(files):
        for block in FENCE_RE.findall(path.read_text(encoding="utf-8")):
            rel = path.relative_to(ROOT)
            try:
                parsed = yaml.safe_load(block)
            except yaml.YAMLError as err:
                errors.append(f"{rel}: YAML example does not parse: {err}")
                continue
            for call in _action_calls(parsed):
                service = call["action"].removeprefix("heads_up.")
                count += 1
                if service not in SCHEMAS:
                    errors.append(f"{rel}: unknown action {call['action']}")
                    continue
                try:
                    SCHEMAS[service](call.get("data") or {})
                except vol.Invalid as err:
                    errors.append(f"{rel}: example for {call['action']} is invalid: {err}")
    return errors, count


def _schema_fields(schema: Any) -> set[str]:
    while not hasattr(schema, "schema") or not isinstance(schema.schema, dict):
        schema = schema.validators[0]  # vol.All(Schema, ...)
    return {str(key) for key in schema.schema}


def _documented_fields(page: str, service: str) -> set[str]:
    """Rows of the "| Field |" table in the `## heads_up.<service>` section."""
    fields: set[str] = set()
    in_section = in_table = False
    for line in page.splitlines():
        if line.startswith("## "):
            in_section = line.strip() == f"## `heads_up.{service}`"
            in_table = False
        elif in_section and line.startswith("| Field"):
            in_table = True
        elif in_table and not line.startswith("|"):
            in_table = False
        elif in_table and (m := re.match(r"^\| `([a-z_]+)` \|", line)):
            fields.add(m.group(1))
    return fields


def check_field_parity() -> list[str]:
    import yaml

    from custom_components.heads_up.services import SCHEMAS

    actions_md = ROOT / "docs" / "actions.md"
    services_yaml = ROOT / "custom_components" / "heads_up" / "services.yaml"
    page = actions_md.read_text(encoding="utf-8")
    declared = yaml.safe_load(services_yaml.read_text(encoding="utf-8"))
    errors = []
    for service, schema in SCHEMAS.items():
        in_schema = _schema_fields(schema)
        in_yaml = set((declared.get(service) or {}).get("fields") or {})
        in_docs = _documented_fields(page, service)
        for name, found in (("services.yaml", in_yaml), ("docs/actions.md", in_docs)):
            if found != in_schema:
                errors.append(
                    f"{name}: {service} fields differ from schema: "
                    f"missing {sorted(in_schema - found)}, extra {sorted(found - in_schema)}"
                )
    return errors


CARD_JS = ROOT / "custom_components" / "heads_up" / "frontend" / "heads-up-card.js"
CARD_TYPE = "custom:heads-up-card"


def check_card_options(files: list[Path]) -> list[str]:
    import yaml

    match = re.search(r"export const CONFIG_KEYS = \[(.*?)\];", CARD_JS.read_text(), re.DOTALL)
    if not match:
        return [f"{CARD_JS.relative_to(ROOT)}: CONFIG_KEYS not found"]
    in_card = set(re.findall(r'"([a-z_]+)"', match.group(1)))

    page = (ROOT / "docs" / "card.md").read_text(encoding="utf-8")
    in_docs: set[str] = set()
    in_table = False
    for line in page.splitlines():
        if line.startswith("| Option"):
            in_table = True
        elif in_table and not line.startswith("|"):
            in_table = False
        elif in_table and (m := re.match(r"^\| `([a-z_]+)` \|", line)):
            in_docs.add(m.group(1))
    errors = []
    if in_docs != in_card:
        errors.append(
            "docs/card.md: options differ from CONFIG_KEYS: "
            f"missing {sorted(in_card - in_docs)}, extra {sorted(in_docs - in_card)}"
        )

    for path in human_docs(files):
        for block in FENCE_RE.findall(path.read_text(encoding="utf-8")):
            try:
                parsed = yaml.safe_load(block)
            except yaml.YAMLError:
                continue  # reported by check_examples
            for card in _card_configs(parsed):
                unknown = set(card) - in_card - {"type"}
                if unknown:
                    rel = path.relative_to(ROOT)
                    errors.append(f"{rel}: card example uses unknown options {sorted(unknown)}")
    return errors


def _card_configs(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, list):
        return [c for item in node for c in _card_configs(item)]
    if isinstance(node, dict):
        found = [node] if node.get("type") == CARD_TYPE else []
        return found + [c for v in node.values() for c in _card_configs(v)]
    return []


def main() -> int:
    sys.path.insert(0, str(ROOT))
    import homeassistant  # noqa: F401  installs the probatio voluptuous shim (HA_API_NOTES N-24)

    files = markdown_files()
    errors = check_words(files)
    example_errors, examples = check_examples(files)
    errors += example_errors + check_field_parity() + check_card_options(files)
    for e in errors:
        print(e)
    print(f"docs-check: {len(files)} files, {examples} examples validated, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
