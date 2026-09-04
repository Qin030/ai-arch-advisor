---
description: 收工檢查
---

執行今日收工檢查，逐項回報。

1. `git checkout main && git pull`
2. `make lint` — 綠？
3. `make test` — 綠？
4. `make demo` — 端到端跑得動？（實際跑一次完整情境：臺南兩層透天）
5. `gh pr list` — 今天開的 PR 有沒有還沒合併的？列出來
6. `python scripts/validate_kb.py` — 知識庫合規？

任何一項紅燈 → **這是今天最優先的事**，先修再下班。規劃書明訂「綠燈才能下班」。

7. 需要的話更新 `docs/STATE.md`：只改日期／階段、契約狀態、已知未補這幾項
   機器查不到的東西。**不要寫 PR 編號、issue 編號、誰在等誰**——那些會過
   時，`/start` 會直接查 GitHub 取得即時狀態。這份檔案內容穩定，變更走
   PR 不痛，但也因此更沒理由塞進會變的東西。

最後產出三行摘要：

```
main 狀態：
未合併 PR：
明天第一件事：
```
