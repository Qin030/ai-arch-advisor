# 變更紀錄

給人看的，不是 git log 的複製。每筆寫「改了什麼」與「為什麼」。
M2 的企畫書稽核就是審這一份——每一筆新增的宣稱，都要能在這裡找到對應的實作。

## [未發布]

### D1
- 契約草擬（**尚未凍結**）：`schema/requirement.schema.json` 與 `docs/CONTRACT.md` 由 M1 草擬，等待 M2 依企畫書附錄獨立審核後才 approve；見 `docs/CONTRACT.md` 開頭的待確認項目
- agent 設定就緒：CLAUDE.md、AGENTS.md、兩份巢狀記憶檔、五個指令、兩個 subagent
- CI 三步驟綠燈：ruff → validate_kb → pytest
- 企畫書就位：`docs/proposal/提案書_v3_0828.docx`（含附錄，語意轉譯強化修訂版）——M2 之後對 schema 的附錄核對以此檔為準
- 修正情境一主角定案為「郭先生」：與 Aug 26 舊稿的「王先生」不一致，已與人工核對確認，`docs/CONTRACT.md`、`docs/PLAN.md` 同步改名；舊稿與 `修訂版_2` 兩份移入 `docs/proposal/archive/`
- 修正 `.github/CODEOWNERS` 比對順序：CODEOWNERS 是「最後符合者勝出」而非「最精確者勝出」，原檔把 `/docs/proposal/` 寫在 `/docs/` 前面，會被後面的 `/docs/` 蓋掉，導致企畫書 owner 從 M1 變成 M2——與 `CLAUDE.md` 明訂的「`docs/proposal/` 由 M1 獨佔編輯」相反。已改為廣泛規則在前、特例在後，並用臨時腳本模擬「最後符合者勝出」驗證五個代表路徑後刪除。同時在檔尾加註明：兩人團隊不開 branch protection 的「Require review from Code Owners」，因為 `/app/` 只有單一 owner，作者不能核准自己的 PR，會讓 PR 永遠卡住；改用「Require approvals: 1」達到相同效果
