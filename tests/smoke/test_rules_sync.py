"""Keeps the rule copy in AGENTS.md aligned with docs/agents/RULES.md.

RULES.md is the single source of truth, but Codex cannot follow @-imports, so
AGENTS.md carries a hand-copied summary. Nothing else notices when the two
drift — and drift means Claude Code and Codex are quietly following different
rules, with no symptom until one of them does something the other forbids.

Deliberately checks for the load-bearing phrase of each rule rather than exact
wording: the two files are written at different lengths on purpose, and a
whole-text diff would fail every day until someone deleted this test.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RULES = (ROOT / "docs" / "agents" / "RULES.md").read_text("utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text("utf-8")

# (規則編號, 該規則不可遺失的關鍵字)
RULE_MARKERS = [
    ("1 產出者≠審查者", ["該功能的測試", "approve 自己"]),
    ("2 不得合併", ["merge 一律由人類", "另一位成員"]),
    ("3 不得捏造來源", ["TODO: 待人工查證", "停工"]),
    ("4 拒答是功能", ["拒答", "鄰近地區"]),
    ("5 diff 上限", ["400 行"]),
    ("6 不得越界", ["只改與當前 issue 相關"]),
    ("7 功能凍結", ["D8", "fix:", "docs:"]),
    ("8 語言", ["繁體中文", "commit"]),
    ("9 不確定就停", ["規格不明、契約沒寫", "問人"]),
]


@pytest.mark.parametrize("rule,markers", RULE_MARKERS, ids=[r[0] for r in RULE_MARKERS])
def test_rule_present_in_both_files(rule, markers):
    for m in markers:
        assert m in RULES, f"RULES.md 遺失「{rule}」的關鍵字：{m}"
        assert m in AGENTS, (
            f"AGENTS.md 遺失「{rule}」的關鍵字：{m}\n"
            f"改了 RULES.md 就要同步 AGENTS.md 的內嵌副本。"
        )


def test_rules_file_still_has_nine_rules():
    # 新增第十條卻沒更新 RULE_MARKERS，這個測試會漏掉它。
    headings = [ln for ln in RULES.splitlines() if ln.startswith("## ")]
    assert len(headings) == len(RULE_MARKERS), (
        f"RULES.md 有 {len(headings)} 條規則，但本測試只檢查 {len(RULE_MARKERS)} 條。"
        f"新增規則時要同時更新 RULE_MARKERS 與 AGENTS.md。"
    )
