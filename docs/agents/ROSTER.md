# Agent 名冊與交接規範

## 名冊

| Agent | 屬於 | 職責 | 讀哪個記憶檔 |
|---|---|---|---|
| **Claude Code** | M1 | 核心實作、整合、審 M2 的 PR | `CLAUDE.md` ＋ 巢狀 `app/rules/CLAUDE.md` |
| **Codex** | M2（主）/ M1（輔） | 規格測試、UI、知識庫、腳本 | `AGENTS.md` ＋ 巢狀 `data/kb/AGENTS.md` |
| **Gemini · 切片員** | M2 | 法規原文切片與 metadata | Gem 1（見 `GEMINI.md`） |
| **Gemini · 審查員** | 兩人 | PR diff 與規格一致性 | Gem 2 |
| **Gemini · 守門員** | M2 | 企畫書宣稱稽核 | Gem 3 |

### Claude Code 的子代理

| Subagent | 何時用 |
|---|---|
| `refusal-auditor` | 每次改動 `app/rules/` 之後；D8 凍結前的最終檢查 |
| `pr-reviewer` | 審 M2 的 PR 時，讓審查在獨立 context 進行 |

### Claude Code 的指令

| 指令 | 用途 |
|---|---|
| `/spec <功能>` | 產規格（不寫程式），供 Codex 據以寫測試 |
| `/impl <issue>` | 讀已合併的測試，實作到綠。禁止改測試 |
| `/review <PR>` | 審 M2 的 PR |
| `/kbaudit` | 知識庫來源抽查，產人工查證清單 |
| `/eod` | 收工檢查 |

---

## 該叫誰：情境對照

| 情境 | 叫誰 | 怎麼叫 |
|---|---|---|
| 要開始做一個新功能 | Claude Code | `/spec <功能>` |
| 規格有了，要寫測試 | M2 的 Codex | 「依 `docs/specs/X.md` 寫測試，**不要看實作**」 |
| 測試合併了，要實作 | Claude Code | `/impl #<issue>` |
| 有一批法規原文要進知識庫 | Gemini Gem 1 → Codex | 先切片，再由 Codex 寫進 `data/kb/` |
| 知識庫進來了，要查證 | Claude Code | `/kbaudit`，然後**人工**逐筆開連結核對 |
| M2 送了 PR 過來 | Claude Code | `/review <PR>` 或呼叫 `pr-reviewer` |
| 改了規則層 | Claude Code | 呼叫 `refusal-auditor` |
| UI 要做/要修 | M2 的 Codex | 直接說，Codex 讀 `AGENTS.md` 的 UI 要求 |
| 追問文案讀起來很怪 | Gemini Gem 2 | 貼追問句與提問理由 |
| 企畫書某段要改 | Claude Code | 直接說要改哪一段。**定位語的改動要 M1 本人確認過才能合併**（見 `docs/PLAN.md`〈企畫書歸屬〉） |
| 企畫書要稽核 | Gemini Gem 3（M2 操作） | 貼企畫書段落 ＋ 實作現況 |
| 今天要收工了 | Claude Code | `/eod` |

---

## 交接規範（最重要的一節）

### 唯一規則：agent 之間只透過已合併的 git artifact 交接

Codex 寫的測試，要**合併進 main 之後**，Claude Code 才讀得到、才開始實作。
Gemini 產的切片，要**由人貼進 PR 並合併之後**，才算數。

### 禁止的做法

> 「我把 Claude Code 的輸出複製貼給 Codex，讓它接著做」

不要這樣。理由有三：

1. **沒有版本。** 出錯時無法回溯是哪一版的規格導致的。
2. **沒有 review。** 那段內容沒有經過另一個人的眼睛。
3. **會漂移。** 貼來貼去的過程中，人會不自覺地刪改、補充、簡化。三天後兩個 agent 對同一件事的理解已經不同了，而沒有人知道。

十天的專案最容易死在這裡——第七天發現 UI 和 API 對不上，追查起來誰也說不清當初是怎麼講好的。

### 允許的例外

- **Gemini 的輸出**必須經人手轉移（它不能開 PR）。但轉移的終點是一個 **PR**，不是另一個 agent 的對話框。
- 口頭澄清可以（「這個欄位是必填嗎」），但**任何會影響程式碼的決定，都要落到 issue 或 PR 上**。

### 交接檢查

每次跨 agent 交接前問自己一句：

> 這個東西在 GitHub 上找得到嗎？

找不到 → 先讓它找得到，再交接。

---

## 記憶檔同步

`docs/agents/RULES.md` 是鐵律的唯一真相來源，但它被複製到兩個地方：

| 檔案 | 方式 |
|---|---|
| `CLAUDE.md` | `@docs/agents/RULES.md` 匯入，自動同步 |
| `AGENTS.md` | **手動內嵌副本**，改動時要兩處都改 |
| Gemini 的三個 Gem | **手動更新**，改動時要進 Gemini 後台改 |

PR 模板有一個 checkbox 提醒這件事。改 `RULES.md` 的 PR 若沒有同步改 `AGENTS.md`，審查者應該退回。

---

## 每個階段要改的東西

| 時機 | 改什麼 |
|---|---|
| D8 功能凍結 | `CLAUDE.md` 與 `AGENTS.md` 的「當前階段」那一行改成「功能凍結：只接受 fix: 與 docs:」 |
| 範圍變更 | `docs/SCOPE.md`，並同步 `docs/proposal-gaps.md` |
| 新增拒答規則 | `app/rules/CLAUDE.md` 的情境表 ＋ `tests/spec/test_refusal.py`（M2 改） |
