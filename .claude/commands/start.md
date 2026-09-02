---
description: 開工檢查，回報現在該做什麼
---

回報現在的狀態與下一步。不要開始任何實作。

1. 讀 `docs/STATE.md`
2. `git checkout main && git pull`
3. `gh pr list` 與 `gh issue list --state open`
4. `gh run list --limit 3` 看 CI 最近的結果
5. 對照 `docs/PLAN.md` 中 STATE.md 標示的那一天

輸出：

當前：D_ · 階段 · 契約狀態
main：綠 / 紅（紅的話：什麼壞了）
阻塞：（誰在等誰）
我今天該做：（依 PLAN.md 該天的 M1 任務，逐項列出）
可以開始嗎：（若契約未凍結而任務依賴契約，明說「不能開始」並說明原因）

最後提醒開工前四問：
1. main 是綠的嗎？紅的就先修，其他都不做
2. 現在是第幾天什麼階段？D8 後只收 fix:
3. 這件事有 issue 嗎？有驗收標準嗎？
4. 該誰做、該用哪個 agent？
