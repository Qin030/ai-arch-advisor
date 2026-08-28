# Agent 設定包：安裝說明

十七個檔案，Day 1 花約 40 分鐘裝完。

## 檔案樹

```
CLAUDE.md                          # Claude Code 專案記憶（M1）
AGENTS.md                          # Codex 記憶（兩人共用）
app/rules/CLAUDE.md                # 巢狀：規則層專屬規範
data/kb/AGENTS.md                  # 巢狀：知識庫專屬規範（最嚴格）
.claude/
  settings.json                    # 權限：擋掉 merge 與 force push
  commands/
    spec.md      /spec             # 產規格，不寫程式
    impl.md      /impl             # 實作到綠，禁止改測試
    review.md    /review           # 審 PR
    kbaudit.md   /kbaudit          # 知識庫來源抽查
    eod.md       /eod              # 收工檢查
  agents/
    refusal-auditor.md             # 拒答行為稽核
    pr-reviewer.md                 # 獨立 context 審 PR
docs/agents/
  RULES.md                         # 九條鐵律（唯一真相來源）
  ROSTER.md                        # 名冊、該叫誰、交接規範
  GEMINI.md                        # 三個 Gem 的指令
.github/
  pull_request_template.md
  CODEOWNERS
```

## 安裝步驟

**1. 複製到 repo 根目錄**

```bash
cp -r agent-setup/. /path/to/your-repo/
cd /path/to/your-repo
```

`app/rules/` 與 `data/kb/` 目前只有記憶檔，程式碼還沒進去，這是對的——記憶檔要先於程式碼存在。

**2. 改 CODEOWNERS 的帳號**

把 `@member1` `@member2` 換成兩人真實的 GitHub 帳號。

**3. 設定 branch protection**

GitHub → Settings → Branches → Add rule → `main`：

- Require a pull request before merging（Required approvals: 1）
- Require review from Code Owners
- Require status checks to pass（等 CI 建好後把 `ci` 勾上）
- Do not allow bypassing the above settings ← **這項要勾**，否則 admin 可以直推，規則形同虛設

**4. 驗證 Claude Code 讀到了**

```bash
cd /path/to/your-repo
claude
```

進去之後打 `/memory` 確認 `CLAUDE.md` 與匯入的 `RULES.md` 都在。打 `/permissions` 確認 deny 清單生效——`.claude/settings.json` 的比對語法要看你的版本，若某條沒生效，用 `/permissions` 介面重設一次。

**5. 建三個 Gemini Gem**

打開 `docs/agents/GEMINI.md`，把三段指令分別貼進 Gemini 的 Gem 設定。三個要分開，不要合成一個。

**6. Codex 確認**

Codex 在 repo 根目錄啟動時會自動讀 `AGENTS.md`。進 `data/kb/` 工作時會讀該目錄的 `AGENTS.md`。可以先問它一句「你在這個專案不能做什麼」驗證有讀到。

## 設計說明：為什麼是這樣寫的

**記憶檔寫的是失敗模式，不是專案介紹。** 企畫書八千多字，塞進 `CLAUDE.md` 每次開 session 都在燒 context，而且擋不住任何一種失誤。真正該寫的是這個專案的 agent 會犯什麼錯：捏造法規條號、把該拒答的情況寫成軟性建議、為了讓測試綠而改測試。

**巢狀記憶檔只在需要時載入。** `data/kb/AGENTS.md` 那份最嚴格的禁令，只有在 agent 真的進到知識庫目錄時才會讀到。放在根目錄會稀釋其他規則。

**用工具強制，不靠自律。** `settings.json` 的 deny 清單擋掉 merge 和 force push；CI 的 `validate_kb.py` 擋掉缺 metadata 的切片；branch protection 擋掉直推。凡是能用機器擋的，就不要寫成「請注意」。

**鐵律只有九條。** 寫二十條的下場是一條都不記得。九條裡面只有第三條（不得捏造來源）標了「違反即停工」——其他都是可以討論的。

## 兩件不能省的人工

1. **D4 的知識庫抽查。** `/kbaudit` 只產出待查證清單，**真偽必須人工開連結核對**。這是唯一一件 agent 完全幫不上忙的事，因為要驗證的正是 agent 可能捏造的東西。

2. **D10 的企畫書稽核由 M2 執行。** M1 是作者，審自己的宣稱是自我審查。Gem 3 的立場設定是「預設每句話都可能誇大」——那個立場，作者裝不出來。
