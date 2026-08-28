#!/usr/bin/env python3
"""Knowledge base metadata gate. Runs in CI before pytest.

Every slice must carry its provenance. The whole proposal rests on the claim that
each piece of retrieved information can be traced to a source, a version and a
region — so that claim gets enforced by a machine, not by remembering.

This checks *shape*, not truth. Whether the content actually appears at
source_url is a human job; see data/kb/VERIFIED.md.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "data" / "kb"

REQUIRED = [
    "id",
    "type",
    "title",
    "source_org",
    "source_url",
    "version_date",
    "region",
    "license",
    "content",
]

TYPES = {"regulation", "cost", "climate"}
REGIONS = {"tainan"}
QUOTA = {"regulation": 10, "cost": 8, "climate": 7}

ID_PATTERN = re.compile(r"^(reg|cost|cli)-[a-z]+-\d{3}$")


def check_slice(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text("utf-8"))
    except yaml.YAMLError as e:
        return [f"YAML 解析失敗: {e}"]

    if not isinstance(data, dict):
        return ["檔案內容不是一個 mapping"]

    for field in REQUIRED:
        if field not in data or data[field] in (None, ""):
            errors.append(f"缺少必填欄位: {field}")

    if "id" in data and not ID_PATTERN.match(str(data["id"])):
        errors.append(f"id 格式不符 (應為 reg|cost|cli-地區-三位數): {data['id']}")

    if "id" in data and path.stem != str(data["id"]):
        errors.append(f"檔名 {path.stem} 與 id {data['id']} 不一致")

    if data.get("type") not in TYPES:
        errors.append(f"type 必須是 {TYPES}，得到 {data.get('type')}")

    if data.get("type") and path.parent.name != data.get("type"):
        errors.append(f"檔案放在 {path.parent.name}/ 但 type 是 {data.get('type')}")

    if data.get("region") not in REGIONS:
        errors.append(f"region 必須在白名單 {REGIONS} 內，得到 {data.get('region')}")

    vd = data.get("version_date")
    if vd is not None:
        if isinstance(vd, str):
            try:
                vd = date.fromisoformat(vd)
            except ValueError:
                errors.append(f"version_date 不是 ISO 8601: {vd}")
                vd = None
        if isinstance(vd, date) and vd > date.today():
            errors.append(f"version_date 在未來: {vd}")

    content = data.get("content")
    if isinstance(content, str) and len(content.strip()) < 20:
        errors.append("content 過短，可能是摘要而非原文")

    return errors


def main() -> int:
    if not KB.exists():
        print(f"找不到 {KB}")
        return 1

    files = sorted(KB.rglob("*.yaml")) + sorted(KB.rglob("*.yml"))
    failed = 0
    counts: dict[str, int] = {t: 0 for t in TYPES}
    seen_ids: set[str] = set()

    for path in files:
        rel = path.relative_to(ROOT)
        errors = check_slice(path)

        data = yaml.safe_load(path.read_text("utf-8")) or {}
        sid = str(data.get("id", ""))
        if sid in seen_ids:
            errors.append(f"id 重複: {sid}")
        seen_ids.add(sid)
        if data.get("type") in counts:
            counts[data["type"]] += 1

        if errors:
            failed += 1
            print(f"\n✗ {rel}")
            for e in errors:
                print(f"    {e}")

    print(f"\n檢查 {len(files)} 筆切片，{failed} 筆有問題")
    for t, quota in QUOTA.items():
        print(f"  {t:12} {counts[t]:2}/{quota}")

    if not files:
        # Day 1: the knowledge base is empty on purpose. Passing here keeps CI
        # green from the first commit, which is what makes a red CI meaningful.
        print("\n知識庫尚未建立（D4 的工作），本次檢查通過。")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
