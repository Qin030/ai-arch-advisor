---
description: 讀已合併的規格測試，實作到全綠
---

實作 $ARGUMENTS。

**絕對禁止修改 `tests/spec/` 下的任何檔案。**

那是 M2 依規格獨立撰寫的契約。測試不過代表你的實作錯了，不是測試太嚴。若你確信測試本身有誤，停下來，在回報中說明哪一條、為什麼，由 M1 判斷後透過 issue 請 M2 修改。

步驟：

1. `make test` 看目前失敗的項目
2. 讀相關的 `tests/spec/` 測試（讀，不改）
3. 讀 `docs/specs/` 下對應的規格
4. 實作，只動你負責的目錄（`app/api/` `app/core/` `app/rules/` `app/retrieval/`）
5. `make test` 與 `make lint` 全綠
6. `make demo` 確認端到端沒壞
7. 開 PR，填完整的 PR 模板

收工前檢查：

- [ ] diff 是否 ≤ 400 行？超過就拆
- [ ] 有沒有動到 `tests/spec/`、`data/kb/`、`ui/`、`schema/`？有就退回
- [ ] 有沒有順手改了與這個 issue 無關的東西？
