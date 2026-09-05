# API 與資料契約

**✅ 已凍結（2026-09-02，M2 複審通過，PR #4）。** M2 於 2026-08-29 完成獨立審查（issue #1），最初結論是「不同意凍結」，列出 4 個決定點與 7 項必修問題；PR #4 逐項回應後，M2 於 2026-09-02 複審通過。四個決定點的最終結果：

- `region` 白名單只有 `tainan` —— 同意，執行路徑見下方〈拒答與 HTTP 語意〉
- `site` 用 `anyOf`（地號或使用分區有一個就行）—— 同意
- `smart.scenes` 至少一項才算填 —— 同意
- `project.floors` ~~上限四層~~ **固定為 2 層**（`minimum: 2, maximum: 2`，不是 1–2 的範圍）—— 附錄只有二層示例，無四層依據，見 `docs/SCOPE.md`

此後改動需 M1 與 M2 雙方 approve（見文末〈改契約的程序〉）。

這份文件與 `schema/requirement.schema.json` 是同一件事的兩面：schema 定義**資料**，本文件定義**傳輸**。程式碼有疑義時以這兩份為準。

---

## 設計前提

四個決定了整份契約形狀的前提：

1. **拒答是回傳值，不是錯誤。** 資料不足時 HTTP 仍回 200，`refusals` 陣列有內容，其餘欄位照常產出。企畫書明講「其餘內容照常產出」——不要用 4xx 表達拒答。
2. **追問決策樹由 schema 驅動。** `x-priority`、`x-question`、`x-question-reason` 都在 schema 裡，`question_tree.py` 讀它，不要在 Python 裡重複維護一份追問句。
3. **狀態存在 server。** UI 只持有 `session_id`，不自己累積需求物件。避免兩邊對「目前收斂到哪」有不同認知。
4. **值域限制不等於拒答。** 只有「使用者填了什麼」該用 schema 的 `type`／`required` 驗證失敗（400）；「填的東西合法但系統判斷不了」一律是拒答（200）。`region` 因此不用 `enum` 限制，見下方〈已知的欄位設計取捨〉。

---

## 資料型別

### `Requirement`

即 `schema/requirement.schema.json`。三個範例檔是這份契約的黃金樣本：

| 檔案 | 代表 |
|---|---|
| `minimal.json` | 剛好滿足必填的最小輸入 |
| `complete.json` | 六個欄位群全填（企畫書情境一的郭先生） |
| `refusal_triggered.json` | 缺 `site` 與 `household`，同時觸發兩條拒答 |
| `refusal_region.json` | `region` 不在允許清單，觸發全部法規判定拒答 |
| `refusal_site.json` | 缺 `site`，單獨觸發一條拒答 |
| `refusal_household.json` | 缺 `household`，單獨觸發一條拒答 |
| `refusal_lighting.json` | 缺 `lighting`，單獨觸發一條拒答 |
| `refusal_smart.json` | 缺 `smart`，單獨觸發一條拒答 |

六個必測拒答情境（見 `app/rules/CLAUDE.md`）裡，只有五個能用 request 範例示範——「成本資料版本過期」判斷的是知識庫切片的 metadata，不是使用者輸入，沒有對應的 request 欄位可以在這裡示範，測試落在檢索／rules 層而非這份契約。

### `Refusal`

拒答的四欄位。**四項缺一不可**，它們直接組成「待專業人員確認清單」的一列。

```json
{
  "missing_field": "site.land_number",
  "confirm_with": "建築師",
  "impact": "可建樓地板面積與樓層數",
  "reason": "未提供地號或使用分區，無法取得適用之建蔽率與容積率",
  "blocks": ["building_coverage_ratio", "floor_area_ratio", "setback"]
}
```

`blocks` 列出因此不生成的輸出欄位，供轉譯層知道哪些段落要跳過。

### `Question`

```json
{
  "field": "lighting",
  "text": "主要生活空間希望偏暖黃、中性白，還是冷白？光感偏明亮還是柔和？",
  "reason": "影響燈具選型與迴路配置，事後變更可能涉及天花與線路調整。",
  "options": [
    { "value": "warm", "label": "暖黃（2700–3000K）" },
    { "value": "neutral", "label": "中性白（3500–4000K）" },
    { "value": "cool", "label": "冷白（5000K 以上）" }
  ],
  "multi": false
}
```

`field` 帶的是 `x-ask-order` 的**欄位群名稱**（如 `lighting`），不是葉欄位
（如 `lighting.color_temp`）。`x-ask-order` 六組各對應一題，一題可以一次
回答該群底下的多個欄位——例如上面這題同時涵蓋 `color_temp` 與
`brightness_preference`。

**一組可能同時有數字、單選、複選、布林等多種葉欄位，但 `Question` 只有
一組 `options`／`multi`。** 不擴充 `Question` 的結構去描述每個子欄位各自
的控制項——UI 依 `field`（群組名稱）硬編碼固定表單，`options`／`multi`
只代表該群裡「主要」的那個列舉型欄位；其餘葉欄位（自由文字、數字、布林
開關、次要的列舉欄位）由 UI 依下表固定渲染，不在 `Question` 回應裡描述：

| 群組 | `options`／`multi` 代表的主要欄位 | 該群另外固定渲染的欄位（不在 `Question` 裡） |
|---|---|---|
| `site` | 無（無列舉欄位，`options: []`, `multi: false`） | `land_number`、`zoning`（文字，至少一項）、`district`（文字，選填） |
| `household` | `routines`（複選，選填） | `members`（數字，必填）、`has_elderly`／`has_children`（布林，選填） |
| `budget` | `includes`（複選，選填） | `total_twd`（數字，選填） |
| `lighting` | `color_temp`（單選，必填，即上方範例） | `brightness_preference`（單選，選填）、`dimmable`／`scene_control`（布林，選填） |
| `circulation` | `priorities`（複選，選填） | `storage_locations`（複選，選填） |
| `smart` | `scenes`（複選，必填，至少 1 項） | `control_mode`（單選，必填）、`devices`（複選，選填） |

每組的完整問題文案、每個欄位的選項與人類可讀標籤，見
`docs/specs/translation-tree.md`——這份契約只定義哪個欄位進 `Question`
信封，不重複列每個選項的文案。

`reason` 是必填。企畫書寫「每題均附提問理由」，這是產品定位的一部分，不是選配。

### `Citation`

```json
{
  "slice_id": "reg-tainan-003",
  "source_org": "法務部全國法規資料庫",
  "source_url": "https://...",
  "version_date": "2026-03-15",
  "region": "tainan",
  "stale": false
}
```

任何引用外部資料的陳述都要帶 citation。`stale: true` 時 UI 顯示過期警示。

---

## Endpoints

Base：`http://localhost:8000`

### `POST /session/start`

開始一次諮詢。

**Request**
```json
{ "utterance": "我想蓋一棟兩層樓的透天厝，預算大概 2000 萬，採光要好、夏天不要太熱，希望有溫暖溫馨的感覺" }
```

**Response 200**
```json
{
  "session_id": "sess-min-001",
  "requirement": { "session_id": "sess-min-001", "region": "tainan" },
  "detected_aspects": ["lighting", "circulation", "climate"],
  "next_question": { "field": "site", "text": "...", "reason": "...", "options": [], "multi": false },
  "progress": { "answered": 0, "total": 6 }
}
```

`detected_aspects` 是理解層辨識出的面向，**不寫入摘要**。企畫書明講「不直接將感受寫入摘要」。

### `POST /turn`

回答一題，取得下一題。

**Request**
```json
{
  "session_id": "sess-min-001",
  "field": "lighting",
  "value": { "color_temp": "warm", "brightness_preference": "soft" }
}
```

`field` 是欄位群名稱，不是葉欄位（見上方 `Question` 一節）。`value` 是物件，
key 是該群底下要回答的葉欄位名稱；每個 key 的型別依 schema 而定：單選是
字串，複選是陣列，數字是數字，布林開關是布林值。同一群裡沒填的葉欄位視為
留白，不等於整題跳過。

**Response 200**
```json
{
  "requirement": { },
  "next_question": { },
  "progress": { "answered": 3, "total": 6 },
  "done": false
}
```

`done: true` 代表 `x-ask-order` 六組都已經處理過一次，可以呼叫
`/summary`。**`/turn` 的流程只前進、不重問**——同一組在這個迴圈裡最多
出現一次，`progress`／`done` 的計算完全依照這個規則，與「有沒有跳過」
無關。

**「處理過」跟「格式錯誤」是兩件不會同時發生的事，不要混在一起講：**

- `value` 不符合схема型別（例如不是物件、必要的 key 型別不對）→ 這個
  請求在進入 session 邏輯之前就被拒絕，回 400（見〈錯誤〉一節），
  **這一組完全沒有被處理**，`progress`／`done` 都不會變，客戶端要用
  正確格式重新送出同一組。
- `value` 型別正確、但內容空白或不完整（例如必填的葉欄位留空字串）→
  這個請求會成功進入 session 邏輯，回 200，**視為已處理，正常前進**。
  D2／D3 都不檢查「填的東西夠不夠格」，那是拒答與結束前需求掃描
  （D5）的工作，不是 `/turn` 這一層要做的判斷。

**跳過一題**：`{"session_id": "...", "field": "budget", "skip": true}`。
跳過**不會**讓 `/turn` 在之後重新問這一組——那是另一個機制：跳過的必填
欄位會出現在 `/summary` 的 `scan.missing` 與 `confirmations`（D5 的結束
前需求掃描，見 `docs/SCOPE.md`〈做（十項）〉#7），讓使用者在看摘要時知道
還有什麼沒填，而不是被追問流程本身問第二次。**這個掃描不算進
`docs/SCOPE.md` 的「5–7 題」——那個數字只計 `x-ask-order` 的六組。**

### `POST /summary`

產出三份文件。

**Request**
```json
{ "session_id": "sess-min-001" }
```

**Response 200**
```json
{
  "session_id": "sess-min-001",
  "scan": {
    "filled": ["region", "household.members", "lighting.color_temp"],
    "assumed": [],
    "missing": ["site.land_number", "budget.total_twd"]
  },
  "building_summary": {
    "sections": [
      { "title": "基地與規模", "content": "…", "citations": ["reg-tainan-003"] }
    ]
  },
  "digital_summary": { "sections": [] },
  "confirmations": [
    {
      "missing_field": "site.land_number",
      "confirm_with": "建築師",
      "impact": "可建樓地板面積與樓層數",
      "reason": "未提供地號或使用分區，無法取得適用之建蔽率與容積率",
      "blocks": ["building_coverage_ratio", "floor_area_ratio", "setback"]
    }
  ],
  "plans": [
    {
      "label": "A",
      "structure": "RC 構造，標準外牆與鋁窗配置",
      "cost_range": "主體約 1,080–1,320 萬元（18–22 萬元／坪）",
      "thermal_relative": "基準",
      "pending": ["地質條件", "基地退縮及鄰棟條件"],
      "citations": ["cost-tainan-002"]
    }
  ],
  "citations": []
}
```

`scan` 的三種狀態對應企畫書「已填、可推定但未確認、缺漏」。

### `GET /health`

`{"status": "ok", "kb_slices": 25, "region_allowlist": ["tainan"]}`

Day 1 只有這一個 endpoint 是真的，其餘回 501。`/health` 是 `make demo` 在 Day 1 唯一檢查的東西。

---

## 錯誤

| 狀態 | 時機 |
|---|---|
| 200 | 正常，**含拒答的情況** |
| 400 | 請求格式不符 schema |
| 404 | `session_id` 不存在或已過期 |
| 501 | 該 endpoint 尚未實作（Day 1–D2 期間的正常回應） |

**沒有「資料不足」的錯誤碼。** 那是 200 加 `confirmations`。

---

## 分階段實作

| 日 | 狀態 |
|---|---|
| D1 | `/health` 真的；其餘 501 |
| D2 | 三個 endpoint 回 `schema/examples/` 的固定假資料 |
| D3 | `/session/start` 與 `/turn` 接真的追問決策樹 |
| D5 | 拒答與掃描接真的規則層 |
| D6 | `/summary` 產真的三份文件 |
| D7 | `plans` 接真的方案比較 |

**UI 從 D2 起就寫死呼叫這三個 endpoint，不隨階段改。** 後端換掉假資料時 UI 一行都不用動——`ui/client.py` 是唯一的接觸點。

---

## 已知的欄位設計取捨

出自 issue #1 M2 審查，決定後記在這裡，避免下次改動時重新爭論一次。

**`region` 不用 `enum`。** 早期草稿把允許清單寫在 schema 的 `enum` 裡，非臺南的請求會被 FastAPI／pydantic 在進入業務邏輯前就擋掉，回 422——但〈設計前提〉第 1 條規定拒答一律 200。改法：schema 的 `region` 只宣告 `type: string`，允許清單移到 `app/core/config.py` 的 `region_allowlist`，由 rules 層比對後產生標準四欄位拒答；`x-refusal` 留在 schema 當文件，不當驗證規則用。

**`budget.total_twd` 維持單值，不改成區間。** 企畫書附錄用「預算區間」描述，但使用者實際說的是「大概兩千萬」這種點估計，改成要求輸入上下限會讓追問從 5–7 題變多題，超出 MVP 的追問題數預算。改法：輸入收單值（`x-question` 已加註「大概的數字就好」），成本推估時由 rules 層套 `±15%` 產生輸出區間——輸入是點、輸出是區間，也更誠實地反映使用者本來就給不出精確區間這件事。

---

## 改契約的程序

1. 開 issue 說明為什麼要改
2. 同時修改 `schema/requirement.schema.json` 與本文件
3. PR 需 M1 與 M2 **雙方** approve（CODEOWNERS 已設定）
4. 在 `docs/CHANGELOG.md` 記一筆

D8 功能凍結後，契約不再變更。

---

## 受機器保護的條款

以下規定由 `tests/smoke/test_contract_guards.py` 強制，改動會讓 CI 紅燈：

- 拒答用 200 回應，沒有「資料不足」的錯誤碼
- 拒答回傳值必含 missing_field / confirm_with / impact / reason
- `region` 白名單只有 `tainan`
- 契約文字不得出現跨區推定的措辭
- schema 中 site / household / lighting / smart 的 `x-refusal` 必須存在

要改這些不是不行，但要在 PR 描述說明為什麼，並同步改測試。
讓 CI 紅燈然後刪測試——不行。
