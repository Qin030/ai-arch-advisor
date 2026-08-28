# AI 建築前期決策助理

把一般人「想要溫馨的家」這類感受語彙，轉譯為可設計條件，產出**建築需求摘要**、
**家庭數位生活需求摘要**與**待專業人員確認清單**三份文件。

系統不取代專業判斷。資料不足、來源衝突或適用地區未收錄時不作判定，轉列待確認事項。

## 跑起來

```bash
cp .env.example .env      # 填入 API key
make install
make demo                 # 端到端 smoke test，收工前必須綠燈
make dev                  # 起 API（另開終端機跑 make ui）
```

## 文件

| 想知道 | 看哪份 |
|---|---|
| API 與資料契約 | `docs/CONTRACT.md` |
| MVP 做什麼、不做什麼 | `docs/SCOPE.md` |
| 十天分工與每日任務 | `docs/PLAN.md` |
| 每個檔案為什麼存在 | `docs/REPO_STRUCTURE.md` |
| Agent 該怎麼用 | `docs/agents/ROSTER.md` |
| 所有 agent 共用的鐵律 | `docs/agents/RULES.md` |

## 現況

Day 1：契約凍結。`/health` 可用，其餘 endpoint 回 501。

<!-- D10 補：功能清單、實測指標、Demo 影片連結、已知限制 -->
