"""D3 follow-up decision tree. Reads the schema; keeps no second copy of it.

docs/CONTRACT.md 〈設計前提〉2: x-ask-order / x-question / x-question-reason live
in schema/requirement.schema.json and this module reads them. A question added
here instead of there is exactly the drift that rule exists to stop.

〈設計前提〉3: the state lives on the server. The UI holds a session_id and
nothing else, so _SESSIONS below is the requirement as it accumulates. In memory
on purpose — a D3 session does not need to survive a restart, and a real store
is not on the plan.

What this module does not do: judge whether an answer is *enough*. Blank and
partial answers move the flow forward (docs/specs/translation-tree.md 二 step 3);
what is missing surfaces in D5's pre-summary scan, not here.
"""

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from app.core.models import (
    Progress,
    Question,
    QuestionOption,
    RequirementDraft,
    StartResponse,
    TurnResponse,
)
from app.core.translator import detect_aspects

ROOT = Path(__file__).resolve().parents[2]

_schema = json.loads((ROOT / "schema" / "requirement.schema.json").read_text("utf-8"))
ASK_ORDER: list[str] = _schema["x-ask-order"]

# The one enum field each group's Question carries options for. Every other leaf
# is rendered by the UI from the group name — docs/CONTRACT.md 〈Question〉 and
# docs/specs/translation-tree.md 三. site has no enum field at all.
_PRIMARY_FIELD: dict[str, str | None] = {
    "site": None,
    "household": "routines",
    "budget": "includes",
    "lighting": "color_temp",
    "circulation": "priorities",
    "smart": "scenes",
}

# Option labels, from docs/specs/translation-tree.md 三 — lighting from
# docs/CONTRACT.md's Question example, which spells the colour temperatures out.
# Only labels live here; values are read from the schema's enum below, so the two
# cannot drift. A value with no label raises at import rather than shipping a
# blank radio button.
_OPTION_LABELS: dict[str, dict[str, str]] = {
    "household": {
        "remote_work": "常在家工作",
        "cooking_often": "常下廚",
        "entertaining": "常招待訪客",
        "pets": "有寵物",
    },
    "budget": {
        "land": "土地",
        "structure": "營造費",
        "interior": "室內裝修",
        "landscape": "景觀外構",
    },
    "lighting": {
        "warm": "暖黃（2700–3000K）",
        "neutral": "中性白（3500–4000K）",
        "cool": "冷白（5000K 以上）",
    },
    "circulation": {
        "short_path": "動線短",
        "storage": "收納充足",
        "automation": "自動化控制",
        "accessibility": "無障礙",
    },
    "smart": {
        "arrive_home": "回家",
        "leave_home": "離家",
        "sleep": "睡眠",
        "security": "安全監控",
        "lighting": "智慧照明",
    },
}


class UnknownSession(KeyError):
    """session_id 不存在或已過期 — docs/CONTRACT.md 〈錯誤〉 404."""


class InvalidAnswer(ValueError):
    """`value` does not match the schema's declared types — 〈錯誤〉 400."""


def _build_options(group: str) -> tuple[list[QuestionOption], bool]:
    primary = _PRIMARY_FIELD[group]
    if primary is None:
        return [], False
    leaf = _schema["properties"][group]["properties"][primary]
    multi = leaf["type"] == "array"
    values = leaf["items"]["enum"] if multi else leaf["enum"]
    labels = _OPTION_LABELS[group]
    return [QuestionOption(value=value, label=labels[value]) for value in values], multi


def _question(group: str) -> Question:
    options, multi = _build_options(group)
    return Question(
        field=group,
        text=_schema["properties"][group]["x-question"],
        reason=_schema["properties"][group]["x-question-reason"],
        options=options,
        multi=multi,
    )


QUESTIONS: dict[str, Question] = {group: _question(group) for group in ASK_ORDER}


# --- answer type checking -----------------------------------------------------

_JSON_TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _type_ok(value: object, declared: str) -> bool:
    if declared == "boolean":
        return isinstance(value, bool)
    if declared in ("integer", "number"):
        # bool subclasses int in Python; JSON Schema does not agree, and letting
        # `true` through as a member count would be a silent wrong answer.
        return isinstance(value, _JSON_TYPES[declared]) and not isinstance(value, bool)
    return isinstance(value, _JSON_TYPES[declared])


def _check_types(group: str, value: object) -> None:
    """Raise InvalidAnswer if `value` does not match the schema's declared types.

    Types only. required / minLength / minItems / anyOf are completeness rules,
    and docs/specs/translation-tree.md 二 step 3 says an incomplete answer is
    still a processed turn — the gap surfaces in D5's scan. See issue #22; if
    that lands the other way, this function is where it changes.
    """
    if not isinstance(value, dict):
        raise InvalidAnswer(
            f"value 必須是欄位群物件，得到 {type(value).__name__}。"
            "一題涵蓋該群底下的多個葉欄位，見 docs/CONTRACT.md 的 Question 一節"
        )

    properties = _schema["properties"][group]["properties"]
    for key, item in value.items():
        leaf = properties.get(key)
        if leaf is None:
            # The schema does not close these groups, so an unrecognised key is
            # not a type error. It is simply not part of the requirement.
            continue
        declared = leaf["type"]
        if not _type_ok(item, declared):
            raise InvalidAnswer(
                f"{group}.{key} 必須是 {declared}，得到 {type(item).__name__}: {item!r}"
            )
        if declared == "array":
            item_type = leaf["items"]["type"]
            for element in item:
                if not _type_ok(element, item_type):
                    raise InvalidAnswer(
                        f"{group}.{key} 的元素必須是 {item_type}，"
                        f"得到 {type(element).__name__}: {element!r}"
                    )


# --- sessions -----------------------------------------------------------------


@dataclass
class _Session:
    # How many of x-ask-order's groups have been processed. Only ever goes up:
    # docs/specs/translation-tree.md 二 — the loop advances, it never re-asks.
    served: int = 0
    answers: dict[str, dict] = field(default_factory=dict)


_SESSIONS: dict[str, _Session] = {}


def has_session(session_id: str) -> bool:
    return session_id in _SESSIONS


def _draft(session_id: str, session: _Session) -> RequirementDraft:
    return RequirementDraft(
        session_id=session_id,
        # D3 does not read the region off the utterance yet. D5's rules layer
        # compares it against app.core.config's region_allowlist and refuses
        # when it is not covered; until then every session is the MVP's region.
        region="tainan",
        **session.answers,
    )


def start_session(utterance: str) -> StartResponse:
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    session = _Session()
    _SESSIONS[session_id] = session
    return StartResponse(
        session_id=session_id,
        requirement=_draft(session_id, session),
        # Detected aspects are shown back to the user, not written into the
        # summary, and they do not change what gets asked — 企畫書 is explicit
        # that feelings are not transcribed into the output.
        detected_aspects=detect_aspects(utterance),
        next_question=QUESTIONS[ASK_ORDER[0]],
        progress=Progress(answered=0, total=len(ASK_ORDER)),
    )


def take_turn(
    session_id: str, value: dict | None = None, skip: bool = False
) -> TurnResponse:
    session = _SESSIONS.get(session_id)
    if session is None:
        raise UnknownSession(session_id)

    done = session.served >= len(ASK_ORDER)
    if not done:
        group = ASK_ORDER[session.served]
        # The flow is positional: the answer belongs to the group the loop is on.
        # `field` in the request says what the client thinks it is answering; a
        # disagreement is not defined by the contract, so it is not enforced.
        if not skip and value is not None:
            _check_types(group, value)
            session.answers[group] = value
        session.served += 1
        done = session.served >= len(ASK_ORDER)

    return TurnResponse(
        requirement=_draft(session_id, session),
        next_question=None if done else QUESTIONS[ASK_ORDER[session.served]],
        progress=Progress(answered=session.served, total=len(ASK_ORDER)),
        done=done,
    )
