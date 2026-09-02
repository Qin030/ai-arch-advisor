# Codex 常用提示詞

Codex 沒有 slash command，以下直接複製貼上。Claude Code 用 `/start`、`/eod` 等指令即可。

## 開工

```
先讀 docs/STATE.md 和 AGENTS.md 的開工程序，回報現在的狀態與你今天該做什麼。
不要開始實作，等我確認。
```

## 收工

```
今天收工。做三件事：
1. 列出你今天開的所有 PR 與目前狀態
2. 列出沒做完的部分，以及明天要從哪裡接續
3. 如果 docs/STATE.md 需要更新，寫出建議的修改內容給我，不要自己改檔案
```

## 寫規格測試（D3、D5）

```
依 docs/specs/<檔名>.md 撰寫 tests/spec/ 的測試。

絕對禁令：不要閱讀 app/rules/、app/core/、app/retrieval/ 的任何實作程式碼。
只能讀 docs/CONTRACT.md、schema/、以及上面那份規格。
規格不足以寫出測試就停下來列出缺什麼，不要去看實作補齊。
```

## 知識庫切片（D4）

```
進 data/kb/ 之前先讀該目錄的 AGENTS.md。
你不得撰寫任何法規條文、統計數字或氣候數據，只能整理我貼給你的原文。
找不到原文就寫 TODO: 待人工查證，並在回報中列出來。
```

## UI（D2、D6、D7）

```
依 AGENTS.md 的 UI 要求實作。三個畫面 D9 要截圖放進企畫書，
不要用 emoji 當圖示，不要用未經設計的預設配色。
```
