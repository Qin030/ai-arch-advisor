"""Vocabulary translation: the opening utterance -> the aspects it mentions.

docs/specs/translation-tree.md 一 defines three vocabulary classes. The word
lists are not repeated here: they live in each group's `description` in
schema/requirement.schema.json as `對應語彙：…`, and this module reads them, the
same way question_tree.py reads x-question. Two copies of a word list drift, and
the schema is the one M2's spec tests read.

What this does NOT do: change the follow-up flow. All six groups get asked in
x-ask-order whether or not their aspect was detected — docs/specs/
translation-tree.md 一 is explicit that detected aspects are for showing the
user what was understood, nothing more.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_schema = json.loads((ROOT / "schema" / "requirement.schema.json").read_text("utf-8"))

_VOCAB_PREFIX = "對應語彙："

# group -> the words that map an utterance onto it. Built from the schema, so a
# group gains vocabulary by editing its description there, not by editing this.
_VOCABULARY: dict[str, tuple[str, ...]] = {
    group: tuple(
        word.strip()
        for word in prop["description"][len(_VOCAB_PREFIX) :].split("、")
        if word.strip()
    )
    for group, prop in _schema["properties"].items()
    if isinstance(prop, dict) and str(prop.get("description", "")).startswith(_VOCAB_PREFIX)
}

if not _VOCABULARY:
    raise RuntimeError(
        "schema 裡找不到任何 對應語彙： 的群組描述——語彙表是這個模組的唯一來源，"
        "不要改成在 Python 裡寫死一份"
    )


def detect_aspects(utterance: str) -> list[str]:
    """Aspects mentioned in the opening utterance, in x-ask-order.

    Substring matching on the schema's word lists. docs/specs/
    translation-tree.md 一 allows synonyms beyond the listed words and
    deliberately leaves other aspects (climate, say) undefined, so this is a
    floor, not a closed set — callers must not treat an empty list as "the user
    said nothing meaningful".
    """
    return [
        group
        for group in _schema["x-ask-order"]
        if group in _VOCABULARY and any(word in utterance for word in _VOCABULARY[group])
    ]
