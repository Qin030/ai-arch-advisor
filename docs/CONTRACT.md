# API 與資料契約

**⚠️ 尚未凍結，等待 M2 審核。** 這份 schema 目前是 M1 直接草擬、由 M1 的 agent 整理的——規劃書原本要求的「M2 從企畫書附錄抽出六個欄位群」這一步被跳過了。凍結程序：M2 拿企畫書附錄獨立對一遍 `schema/requirement.schema.json`，不同意的地方開 issue，而不是直接 approve。以下四項需要 M2 明確表態，寫死進 schema 後 D3 起再改就要動測試：

- `region` 白名單只有 `tainan`
- `site` 用 `anyOf`（地號或使用分區有一個就行）
- `smart.scenes` 至少一項才算填
- `project.floors` 上限四層

M2 review 通過並 approve 後，才算 Day 1 凍結；此後改動需 M1 與 M2 雙方 approve（見文末〈改契約的程序〉）。

這份文件與 `schema/requirement.schema.json` 是同一件事的兩面：schema 定義**資料**，本文件定義**傳輸**。程式碼有疑義時以這兩份為準。

---

## 設計前提

三個決定了整份契約形狀的前提：

1. **拒答是回傳值，不是錯誤。** 資料不足時 HTTP 仍回 200，`refusals` 陣列有內容，其餘欄位照常產出。企畫書明講「其餘內容照常產出」——不要用 4xx 表達拒答。
2. **追問決策樹由 schema 驅動。** `x-priority`、`x-question`、`x-question-reason` 都在 schema 裡，`question_tree.py` 讀它，不要在 Python 裡重複維護一份追問句。
3. **狀態存在 server。** UI 只持有 `session_id`，不自己累積需求物件。避免兩邊對「目前收斂到哪」有不同認知。

---

## 資料型別

### `Requirement`

即 `schema/requirement.schema.json`。三個範例檔是這份契約的黃金樣本：

| 檔案 | 代表 |
|---|---|
| `minimal.json` | 剛好滿足必填的最小輸入 |
| `complete.json` | 六個欄位群全填（企畫書情境一的郭先生） |
| `refusal_triggered.json` | 缺 `site` 與 `household`，觸發兩條拒答 |

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
  "field": "lighting.color_temp",
  "text": "主要生活空間希望偏暖黃、中性白，還是冷白？",
  "reason": "影響燈具選型與迴路配置，事後變更可能涉及天花與線路調整。",
  "options": [
    { "value": "warm", "label": "暖黃（2700–3000K）" },
    { "value": "neutral", "label": "中性白（3500–4000K）" },
    { "value": "cool", "label": "冷白（5000K 以上）" }
  ],
  "multi": false
}
```

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
  "next_question": { "field": "site.zoning", "text": "...", "reason": "...", "options": [], "multi": false },
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
  "field": "lighting.color_temp",
  "value": "warm"
}
```

`value` 型別依 schema 而定：單選是字串，複選是陣列，數字是數字。

**Response 200**
```json
{
  "requirement": { },
  "next_question": { },
  "progress": { "answered": 3, "total": 6 },
  "done": false
}
```

`done: true` 代表追問結束（所有必填已填，或使用者標記「不需要」），可以呼叫 `/summary`。

**跳過一題**：`{"session_id": "...", "field": "budget.total_twd", "skip": true}`。跳過的必填欄位會在結束前掃描時再問一次，仍不填則轉列待確認。

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

## 改契約的程序

1. 開 issue 說明為什麼要改
2. 同時修改 `schema/requirement.schema.json` 與本文件
3. PR 需 M1 與 M2 **雙方** approve（CODEOWNERS 已設定）
4. 在 `docs/CHANGELOG.md` 記一筆

D8 功能凍結後，契約不再變更。
