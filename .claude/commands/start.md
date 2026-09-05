---
description: 開工檢查，回報現在該做什麼
---

回報現在的狀態與下一步。不要開始任何實作。

`docs/STATE.md` 只記錄機器查不到的東西（日期、階段、契約狀態、已知未補）。
阻塞、PR 狀態、下一步這些會變的東西，一律即時查 GitHub，不要相信檔案裡
可能寫過的舊內容。

1. 讀 `docs/STATE.md`（日期、階段、契約狀態、已知未補）
2. `git checkout main && git pull`
3. `gh pr list` 與 `gh issue list --state open`
4. `gh run list --limit 3` 看 CI 最近的結果
5. `gh pr list --json number,title,createdAt,reviewDecision` 逐筆檢查
   `createdAt`：開了超過 24 小時、`reviewDecision` 是 `null` 或
   `REVIEW_REQUIRED` 的 PR 全部列出來，標記為需要立刻處理——這是 D1 那次
   PR #3 卡了四天沒人發現的直接對策。（`reviewDecision` 沒有 `PENDING`
   這個值；GitHub 的實際值是 `APPROVED`、`CHANGES_REQUESTED`、
   `REVIEW_REQUIRED` 或 `null`——這個 repo 開了「Required approvals: 1」，
   所以任何還沒拿到核准的 PR 平常就會是 `REVIEW_REQUIRED`，不是
   `null`，只查 `null` 幾乎抓不到東西。）若要更精確判斷「完全沒人看過」
   而不只是「還沒核准」，改查 `gh pr view <n> --json reviews` 是否為空。
6. 對照 `docs/PLAN.md` 中 STATE.md 標示的那一天

輸出：

當前：D_ · 階段 · 契約狀態（讀自 STATE.md）
main：綠 / 紅（紅的話：什麼壞了，讀自 gh run list）
阻塞：（誰在等誰，讀自 gh pr list / gh issue list 的即時狀態）
逾時未審的 PR：（開超過 24 小時仍無 review 的 PR，沒有就說「無」）
我今天該做：（依 PLAN.md 該天的 M1 任務，逐項列出）
可以開始嗎：（若契約未凍結而任務依賴契約，明說「不能開始」並說明原因）

最後提醒開工前四問：
1. main 是綠的嗎？紅的就先修，其他都不做
2. 現在是第幾天什麼階段？D8 後只收 fix:
3. 這件事有 issue 嗎？有驗收標準嗎？
4. 該誰做、該用哪個 agent？
