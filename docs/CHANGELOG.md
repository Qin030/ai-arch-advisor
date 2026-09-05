# 變更紀錄

給人看的，不是 git log 的複製。每筆寫「改了什麼」與「為什麼」。
M2 的企畫書稽核就是審這一份——每一筆新增的宣稱，都要能在這裡找到對應的實作。

## [未發布]

### D2

- 企畫書執筆權移交（2026-09-06，**需 M2 approve**）：`docs/proposal/` 從「M1
  獨佔、agent 不碰」改為由 Claude Code 執筆，M1 保留口徑與定位語的決定權。
  改動原因是 `docs/PLAN.md`〈企畫書歸屬〉的〈代價〉那段本來就承認的問題——
  M1 同時扛組長＋主力開發＋文件作者，4 小時/日不夠。原本列的三個「由 M1
  執筆」的理由，只有第三個（交給別人寫再由 M1 改等於做兩次）真的翻掉，
  另外兩個改寫成執筆的限制：論述線連動 → 改任何一句宣稱前先把連動處列進
  `docs/proposal-gaps.md`；定位語刻意 → **定位語的改動要 M1 本人確認過才能
  合併，這是唯一保留的人工關卡**。同步四處：`CLAUDE.md`〈你的角色〉與
  〈你負責的目錄〉／〈你不得修改〉、`docs/PLAN.md` 的分工表與〈企畫書歸屬〉
  ／目錄歸屬表／〈企畫書的版本控管〉、`docs/agents/ROSTER.md`〈該叫誰〉。
  `.github/CODEOWNERS` 的 `/docs/proposal/ @Qin030` **不變**——owner 仍是 M1，
  且依鐵律 1 作者不能核准自己的 PR，企畫書 PR 仍須 M2 approve
- `docs/CONTRACT.md` 契約澄清（**待 M2 複審**）：`Question.field` 與 `/turn` 的
  `field` 帶的是 `x-ask-order` 的欄位群名稱（如 `lighting`），不是葉欄位
  （如 `lighting.color_temp`）；一次可回答該群底下的多個欄位，`value` 對應
  改成物件。原範例用葉欄位示範請求形狀，但 `docs/SCOPE.md`〈做（十項）〉
  #2 明訂「勾選式追問 5–7 題」，六組展開成葉欄位遠超過 7 題，只有「一題
  等於一組」的讀法對得上——寫 D3 規格（`docs/specs/translation-tree.md`，
  issue #11）時發現這個落差，隨附修正 `Question` 與 `/turn` 的範例。不涉及
  `schema/requirement.schema.json`（該檔未定義 Turn 請求／回應信封的形狀）
- UI 三畫面骨架進 main（PR #16，M2 的 Codex 產出）：智慧追問、多方案比較、
  需求摘要與來源，全部透過 `ui/client.py` 這唯一的 API 邊界呼叫三個
  endpoint。審查時本機把這支分支與假資料 endpoint 合併實跑，抓到一個會擋住
  整個追問流程的問題——送出答案時沒有把值包成契約要求的群組物件，六組全部
  會回 422；M2 補上 `PRIMARY_FIELDS` 對照與 `answer_payload()` 後複測通過
- `docs/STATE.md` 定位修正進 main（PR #10）：這份檔案每次更新都要走保護分支
  的 PR，等合併時裡面寫的 PR／issue 狀態早就過時（該 PR 自己就是例子）。改成
  只留機器查不到的東西（日期／階段、契約狀態、已知未補），PR、issue、CI 的
  即時狀況一律由 `/start` 查 GitHub。`/start` 同時新增「開超過 24 小時仍未
  取得核准的 PR」偵測，作為 D1 那次 PR #3 卡四天沒人發現的對策；`CLAUDE.md`
  與 `AGENTS.md` 裡同一個概念的舊描述一併同步，避免只改一處造成漂移
- `.claude/commands/start.md` 的逾時偵測條件修正（PR #10 內）：原本查
  `reviewDecision` 是否為 `null`／`PENDING`，但 GitHub 沒有 `PENDING` 這個
  值，且本 repo 開了「Required approvals: 1」，未核准的 PR 平常就是
  `REVIEW_REQUIRED`——舊條件對當時開著的五個 PR 一個都抓不到。改為檢查
  `null` 或 `REVIEW_REQUIRED`

### D1
- 契約草擬（**尚未凍結**）：`schema/requirement.schema.json` 與 `docs/CONTRACT.md` 由 M1 草擬，等待 M2 依企畫書附錄獨立審核後才 approve；見 `docs/CONTRACT.md` 開頭的待確認項目
- agent 設定就緒：CLAUDE.md、AGENTS.md、兩份巢狀記憶檔、五個指令、兩個 subagent
- 三個 Gemini Gem（法規切片員、規格與 PR 審查員、企畫書守門員）已依 `docs/agents/GEMINI.md` 手動建立完成
- `@youyiwangwww` 已接受 collaborator 邀請；issue #1（M0 schema 審查）已改指派給她
- `main` 開啟 branch protection：Required approvals 1、不勾 Require review from Code Owners、Required status check `ci`、Do not allow bypassing。三項機制皆以實際測試 PR（#2，已關閉不合併）驗證生效：直推 main 被拒（GH006）、PR 自動指派 reviewer（CODEOWNERS `*` 規則）、merge 因 branch policy 被擋（含 admin 身分）。
- CI 首次在 PR 上執行時發現 flat-layout 套件偵測失敗（根目錄同時有 `app/`、`data/`、`schema/`，setuptools 無法判斷要打包哪個），已在 `pyproject.toml` 明確宣告 `packages`。乾淨環境四步（pip install -e ".[dev]" → ruff → validate_kb → pytest）驗證全綠後才推。**Day 1 完成。**
- 新增 `tests/smoke/test_contract_guards.py`：機器強制 `docs/CONTRACT.md` 中拒答相關的不可退讓條款（200 回應、四欄位齊全、region 白名單、禁止跨區推定措辭、四個欄位群的 `x-refusal` 存在）。目前只驗契約文件與 schema 本身，D5 規則層完成後擴充為端到端驗證。`docs/CONTRACT.md` 補上「受機器保護的條款」一節說明
- 新增 `tests/smoke/test_rules_sync.py`：機器比對 `docs/agents/RULES.md`（唯一真相來源）與 `AGENTS.md` 內嵌副本的九條規則關鍵字，防止兩份文件漂移導致 Claude Code 與 Codex 遵守不同版本的規則。比對語意關鍵字而非逐字，避免因兩份行文長度不同而天天紅燈。`docs/agents/RULES.md` 開頭補上同步提醒
- CI 三步驟綠燈：ruff → validate_kb → pytest
- 企畫書就位：`docs/proposal/提案書_v3_0828.docx`（含附錄，語意轉譯強化修訂版）——M2 之後對 schema 的附錄核對以此檔為準
- 修正情境一主角定案為「郭先生」：與 Aug 26 舊稿的「王先生」不一致，已與人工核對確認，`docs/CONTRACT.md`、`docs/PLAN.md` 同步改名；舊稿與 `修訂版_2` 兩份移入 `docs/proposal/archive/`
- 修正 `.github/CODEOWNERS` 比對順序：CODEOWNERS 是「最後符合者勝出」而非「最精確者勝出」，原檔把 `/docs/proposal/` 寫在 `/docs/` 前面，會被後面的 `/docs/` 蓋掉，導致企畫書 owner 從 M1 變成 M2——與 `CLAUDE.md` 明訂的「`docs/proposal/` 由 M1 獨佔編輯」相反。已改為廣泛規則在前、特例在後，並用臨時腳本模擬「最後符合者勝出」驗證五個代表路徑後刪除。同時在檔尾加註明：兩人團隊不開 branch protection 的「Require review from Code Owners」，因為 `/app/` 只有單一 owner，作者不能核准自己的 PR，會讓 PR 永遠卡住；改用「Require approvals: 1」達到相同效果
- issue #1：M2 於 8/29 完成獨立審查，結論「不同意凍結」，列出 4 個決定點（不同意 `project.floors maximum: 4`，附錄無四層依據）與 7 項必修問題。M1 回應延遲 4 天才處理（PR #3 合併後才發現），在 `fix/schema-m2-review` 分支逐項修正：`region` 拿掉 schema `enum`、改由 `app/core/config.py` 的 `region_allowlist` 於 rules 層比對（避免 422 vs 200 衝突）；`site.land_number`／`zoning` 加 `minLength: 1`（防空字串繞過拒答）；`project.floors` 固定為 2（`minimum: 2, maximum: 2`，採 M2 意見；第一次修正只改 `maximum`、漏改 `minimum`，仍放行一層，經 M2 複審抓到後改用只接受 2 的約束並補守衛測試；中間一度改成 `const: 2` 又依 M2「或等價」的說法改回 min/max，避免擴充樓層數時要動 schema 結構）；`budget.total_twd` 維持單值、`x-question` 加註「大概的數字就好」、輸出區間改在 rules 層產生；`$id` 的 `OWNER` 換成 `Qin030`；成本過期情境（六個必測情境之四）在 `app/rules/CLAUDE.md` 註明由 rules 層依 `Citation.stale` 承載，非 schema 欄位；六個拒答情境中可用 request 示範的五個各補一份 `schema/examples/` 範例。2026-09-02 經 M2 複審通過（PR #4 合併，issue #1 關閉），契約凍結
