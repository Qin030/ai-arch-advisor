"""D2 fixed-response builders for the three endpoints.

Per docs/CONTRACT.md 分階段實作: D2 endpoints return fixed fake data, not real
decisions. /turn walks schema/requirement.schema.json's x-ask-order strictly by
position and ignores the submitted field/value — no judgment. D3 replaces the
walk with the real decision tree; this module is fixture-only scaffolding, not
that tree.
"""

import json
import uuid
from pathlib import Path

from app.core.models import (
    DocumentSection,
    DocumentSummary,
    PlanOption,
    Progress,
    Question,
    QuestionOption,
    Refusal,
    Requirement,
    ScanResult,
    StartResponse,
    SummaryResponse,
    TurnResponse,
)

ROOT = Path(__file__).resolve().parents[2]

_schema = json.loads((ROOT / "schema" / "requirement.schema.json").read_text("utf-8"))
ASK_ORDER: list[str] = _schema["x-ask-order"]

# field = the group key, not a leaf like "site.zoning": one x-question in the
# schema covers a whole group's fields at once, so the group is the real unit
# of a "turn" at this fixture stage.
#
# A group's Question carries exactly one options/multi pair, describing that
# group's "primary" enum field; every other leaf field is rendered by the UI
# from the group name alone. Mapping: docs/CONTRACT.md's Question section and
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
# Only labels live here; the values come from the schema's enum below, so the
# two cannot drift apart silently. A value with no label raises at import time
# rather than shipping a blank radio button.
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


def _build_options(group: str) -> tuple[list[QuestionOption], bool]:
    """Options and the multi flag for one group's primary field.

    Values from the schema's enum, labels from _OPTION_LABELS. An enum gaining a
    value without a label is a KeyError here, at import, not a silent blank.
    """
    field = _PRIMARY_FIELD[group]
    if field is None:
        return [], False
    leaf = _schema["properties"][group]["properties"][field]
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


_QUESTIONS = {group: _question(group) for group in ASK_ORDER}

_TURN_REQUIREMENT = Requirement.model_validate(
    json.loads((ROOT / "schema" / "examples" / "complete.json").read_text("utf-8"))
)

# session_id -> count of groups already served. In-memory only: fixture-stage
# sessions don't need to survive a restart.
_sessions: dict[str, int] = {}


def start_session(utterance: str) -> StartResponse:
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    _sessions[session_id] = 1
    return StartResponse(
        session_id=session_id,
        requirement=Requirement(session_id=session_id, region="tainan"),
        detected_aspects=["lighting", "circulation", "climate"],
        next_question=_QUESTIONS[ASK_ORDER[0]],
        progress=Progress(answered=0, total=len(ASK_ORDER)),
    )


def take_turn(session_id: str) -> TurnResponse:
    if session_id not in _sessions:
        raise KeyError(session_id)
    served = _sessions[session_id]
    if served < len(ASK_ORDER):
        next_question = _QUESTIONS[ASK_ORDER[served]]
        done = False
        _sessions[session_id] = served + 1
    else:
        next_question = None
        done = True
    requirement = _TURN_REQUIREMENT.model_copy(update={"session_id": session_id})
    return TurnResponse(
        requirement=requirement,
        next_question=next_question,
        progress=Progress(answered=served, total=len(ASK_ORDER)),
        done=done,
    )


def build_summary(session_id: str) -> SummaryResponse:
    if session_id not in _sessions:
        raise KeyError(session_id)
    # Canned content lifted verbatim from docs/CONTRACT.md's own /summary
    # example — not invented here, so it doesn't trip the "no fabricated
    # sources" rule. D6 replaces this with real generation.
    return SummaryResponse(
        session_id=session_id,
        scan=ScanResult(
            filled=["region", "household.members", "lighting.color_temp"],
            assumed=[],
            missing=["site.land_number", "budget.total_twd"],
        ),
        building_summary=DocumentSummary(
            sections=[
                DocumentSection(title="基地與規模", content="…", citations=["reg-tainan-003"]),
            ]
        ),
        digital_summary=DocumentSummary(sections=[]),
        confirmations=[
            Refusal(
                missing_field="site.land_number",
                confirm_with="建築師",
                impact="可建樓地板面積與樓層數",
                reason="未提供地號或使用分區，無法取得適用之建蔽率與容積率",
                blocks=["building_coverage_ratio", "floor_area_ratio", "setback"],
            )
        ],
        plans=[
            PlanOption(
                label="A",
                structure="RC 構造，標準外牆與鋁窗配置",
                cost_range="主體約 1,080–1,320 萬元（18–22 萬元／坪）",
                thermal_relative="基準",
                pending=["地質條件", "基地退縮及鄰棟條件"],
                citations=["cost-tainan-002"],
            )
        ],
        citations=[],
    )
