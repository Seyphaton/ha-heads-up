"""Translation files carry the keys and placeholders of strings.json (D-071)."""

import json
import re
from pathlib import Path
from typing import Any

import pytest

TRANSLATIONS = Path(__file__).parent.parent / "custom_components" / "heads_up" / "translations"
PLACEHOLDER = re.compile(r"\{[a-z_]+\}")


def flat(data: dict[str, Any], path: tuple[str, ...] = ()) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            out.update(flat(value, (*path, key)))
        else:
            out[".".join((*path, key))] = value
    return out


SOURCE = flat(json.loads((TRANSLATIONS.parent / "strings.json").read_text(encoding="utf-8")))


def test_english_file_is_a_copy_of_strings_json() -> None:
    english = flat(json.loads((TRANSLATIONS / "en.json").read_text(encoding="utf-8")))
    assert english == SOURCE


@pytest.mark.parametrize("language", ["de", "fr", "es"])
def test_translation_has_every_key_and_placeholder(language: str) -> None:
    translated = flat(json.loads((TRANSLATIONS / f"{language}.json").read_text(encoding="utf-8")))
    assert translated.keys() == SOURCE.keys()
    for key, text in translated.items():
        assert sorted(PLACEHOLDER.findall(text)) == sorted(PLACEHOLDER.findall(SOURCE[key])), key
