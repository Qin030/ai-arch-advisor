"""D2 fixed-response builder for /summary.

Per docs/CONTRACT.md 分階段實作, D2 endpoints returned fixed fake data. D3 took
/session/start and /turn off this and onto the real decision tree in
app.core.question_tree; /summary stays canned until D6 generates the three
documents for real. What is left here is fixture-only scaffolding, not a tree.
"""

from app.core.models import (
    DocumentSection,
    DocumentSummary,
    PlanOption,
    Refusal,
    ScanResult,
    SummaryResponse,
)


def build_summary(session_id: str) -> SummaryResponse:
    """The canned D6 shape. The caller checks the session exists first.

    Content lifted verbatim from docs/CONTRACT.md's own /summary example — not
    invented here, so it does not trip the "no fabricated sources" rule. D6
    replaces this with real generation over the knowledge base.
    """
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
