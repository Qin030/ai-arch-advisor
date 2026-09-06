# 變更紀錄

給人看的，不是 git log 的複製。每筆寫「改了什麼」與「為什麼」。
M2 的企畫書稽核就是審這一份——每一筆新增的宣稱，都要能在這裡找到對應的實作。

## [未發布]

### D2

- **契約修改（依〈改契約的程序〉，需雙方 approve）：**〈設計前提〉4 原本寫「只有『使用者
  填了什麼』該用 schema 的 `type`／`required` 驗證失敗（400）」，與同一份文件〈`POST /turn`〉
  的「型別正確、但內容空白或不完整 → 回 200，視為已處理，正常前進」以及
  `docs/specs/translation-tree.md`〈二〉流程第 3 步互相矛盾。改為只有 `type` 回 400；
  `required`／`minLength`／`minItems`／`anyOf` 是完整性條款，不在 `/turn` 擋欄位群的內容，
  缺漏留給 D5 的結束前掃描。理由：完整性檢查延後是為了允許保留部分回答並繼續收集其他
  需求——一組裡填了一半的答案若被擋成 400，使用者只剩「整組填完」或「整組跳過」兩條路，
  那半筆已知資訊就留不下來；缺漏統一由結束前掃描揭露，只有一個出口。另補一句釐清這條
  講的是欄位群的內容，
  請求信封本身缺欄位（例如沒有 `session_id`）仍是 400。不涉及
  `schema/requirement.schema.json`（該檔未定義 `/turn` 的 HTTP 行為）。出自 issue #22，
  M2 在 #20 的規格測試押的就是這個讀法，#28 的實作也照此
- 企畫書執筆權移交（2026-09-06，**需 M2 approve**）：`docs/proposal/` 從「M1
  獨佔、agent 不碰」改為由 Claude Code 執筆，M1 保留口徑與定位語的決定權。
  改動原因是 `docs/PLAN.md`〈企畫書歸屬〉的〈代價〉那段本來就承認的問題——
  M1 同時扛組長＋主力開發＋文件作者，4 小時/日不夠。原本列的三個「由 M1
  執筆」的理由，只有第三個（交給別人寫再由 M1 改等於做兩次）真的翻掉，
  另外兩個改寫成執筆的限制：論述線連動 → 改任何一句宣稱前先把連動處列進
  `docs/proposal-gaps.md`；定位語刻意 → **定位語的改動要 M1 本人確認過才能
  合併，這是唯一新增的人工關卡**。該關卡的完成條件是兩段：改完先標「已改，
  待 M1 確認措辭」，M1 本人確認並留下紀錄後才改成「已改，M1 已確認措辭」，
  否則仍未完成。它是**額外**的作者確認，**不取代 M2 的宣稱一致性審查與實質
  否決權，也不取代 M2 的 PR 核准與另一位成員的人工合併**——爭議仍須提出實作
  或實測證據並取得 M2 同意（依 M2 在 #25 的複審意見補明確）。同步四處：`CLAUDE.md`〈你的角色〉與
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
- 企畫書口徑修正六項（`docs/proposal/提案書_v3_0828.docx`，**Claude Code 經
  M1 當面授權代改，措辭已由 M1 於 2026-09-06 本人確認**）：知識庫來源清單刪掉未實際收錄的
  「非都市土地使用管制規則及各縣市建築管理自治法規」與「專業公會資料」；
  「第一階段涵蓋六都及鄰近縣市」改為「Prototype 先行驗證臺南市，六都及鄰近
  縣市為第一階段目標」；SAM 口徑加「目標」二字與前句一致；護城河第四點改為
  「已建立逐縣市維護機制，現階段涵蓋臺南市」；「閉環修正」三處（五重信任
  防線、情境二、護城河第二點）全部標為「流程已設計、尚未實作，列為下一
  階段」；部署段從「現階段部署於 Linux＋Docker＋Nginx」改為「現階段於本機
  ⋯⋯環境開發」。`docs/proposal-gaps.md` 對應六列標為已改；第 5、8、9 列
  依賴 D6／D8／D9 的實測資料，刻意不動。改法採 zip 內 `word/document.xml`
  字串替換，每處先驗證只出現一次才替換，改完全部 XML 重新解析通過、段落數
  與檔案清單與原檔一致
- 企畫書口徑修正第二輪（同上檔案，**Claude Code 經 M1 授權代改，措辭已由 M1 於
  2026-09-06 本人確認**）：
  M2 複審 PR #18 時解壓 Word XML 逐段核對，指出第一輪把 `docs/proposal-gaps.md` 第 7 列
  整列標為已改，但該列要求的兩件事只做了一件。三處修正：
  （1）第 173 段「現階段 Prototype 已串接三類知識庫」改為「三類知識庫的切片格式與來源
  清單已定義」，並把「各筆資料標註⋯檢索採關鍵字與向量混合檢索」改為必填欄位規範＋
  「檢索規劃採」，句末補「臺南市切片與檢索層尚在建置中，本階段尚未串接實際資料」——
  `data/kb/` 是 0 筆，`app/retrieval/` 只有 `__init__.py`；
  （2）第 176 段「現階段於本機 Linux＋Docker＋Nginx 環境開發」改為「部署尚未建置，現階段
  僅於本機開發環境執行；規劃採 Linux＋Docker＋Nginx」——repo 內找不到任何 Dockerfile、
  nginx 設定或 compose 檔；
  （3）第 281 段「已建立逐縣市維護⋯機制，現階段涵蓋臺南市」改為「已定義⋯格式與驗證機制
  （每筆切片必填適用地區與版本日期，由 CI 檢查，另設人工查證台帳）；臺南市資料建置中」。
  另依 `docs/proposal-gaps.md`「有新問題就現在加進來」補第 10 列：第 176 段還有四項同類
  宣稱（ChromaDB 向量索引、關聯式資料庫、模型分工、規則層執行拒答）在實作到位前都不成立，
  依鐵律 6 不在本輪順手改，列進表裡由 D10 逐列驗收。改法同第一輪，段落數 373 對 373、
  XML 重新解析通過、zip 23 個項目與原檔一致
- 企畫書措辭確認（2026-09-06）：M1 本人逐段讀過上述兩輪共九處改動，確認措辭，
  `docs/proposal-gaps.md` 第 1、2、3、4、6、7 列狀態由「待 M1 確認措辭」改為
  「M1 已確認措辭」。第 5、8、9 列仍是 `☐`，依賴 D6／D8／D9 的實測資料；第 10 列
  仍是 `☐`，那四項技術堆疊宣稱要等 D4／D5／D6 實作到位才回填。**這道人工關卡不因
  執筆權移交而取消**——#25 明訂定位語的改動仍須 M1 本人確認才能合併
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
