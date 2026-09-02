"""Guards the non-negotiable clauses of docs/CONTRACT.md.

CONTRACT.md is prose. These are the sentences in it that must never quietly
change, because a violation would not surface until the demo or the judges'
Q&A — by which point the whole "可查核、可拒答" premise is already broken.

D5 note: once app/rules/ exists, extend these to assert on real API responses
rather than on the contract text and schema alone.
"""

import re
from pathlib import Path

import pytest

from app.core.config import Settings

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (ROOT / "docs" / "CONTRACT.md").read_text("utf-8")

REFUSAL_FIELDS = ["missing_field", "confirm_with", "impact", "reason"]


def test_refusal_is_a_200_not_an_error():
    # 拒答是回傳值，不是錯誤。改成 4xx 會讓 UI 把它當失敗處理，
    # 「其餘內容照常產出」就做不到了。
    assert "沒有「資料不足」的錯誤碼" in CONTRACT
    assert re.search(r"200.*含拒答", CONTRACT), "錯誤碼表遺失『200 含拒答』"


def test_refusal_declares_all_four_fields(schema):
    for name, prop in schema["properties"].items():
        if isinstance(prop, dict) and "x-refusal" in prop:
            missing = {"confirm_with", "impact", "reason"} - set(prop["x-refusal"])
            assert not missing, f"{name} 的 x-refusal 缺 {missing}"


def test_contract_documents_the_four_refusal_fields():
    for f in REFUSAL_FIELDS:
        assert f in CONTRACT, f"CONTRACT.md 未記載拒答欄位 {f}"


def test_region_allowlist_has_exactly_one_region():
    # 跨區推定是這個產品最不能犯的錯。加地區必須同時加知識庫切片，
    # 所以擴充白名單是刻意的決定，不該悄悄發生。
    #
    # 白名單不再放在 schema 的 enum 裡：enum 驗證失敗會被 FastAPI 轉成
    # 422，但 CONTRACT.md 規定拒答一律 200，所以改成 rules 層依
    # app.core.config.settings.region_allowlist 比對。檢查對象換成
    # config 的宣告值，而不是放寬標準。
    assert Settings.model_fields["region_allowlist"].default == ["tainan"]


def test_no_fallback_inference_language_in_contract():
    # 「查無 A 就用 B」的措辭一旦寫進契約，實作就會跟著做。
    for bad in ["鄰近地區", "類似地區", "參考其他縣市"]:
        assert bad not in CONTRACT, f"契約出現跨區推定措辭：{bad}"


@pytest.mark.parametrize("field", ["site", "household", "lighting", "smart"])
def test_refusal_scenarios_survive_in_schema(schema, field):
    # app/rules/CLAUDE.md 的六個必測情境，有四個由 schema 的 x-refusal 承載。
    # 少了任何一個代表拒答被拿掉了。
    assert "x-refusal" in schema["properties"][field], f"{field} 的拒答定義不見了"
