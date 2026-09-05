# AI 建築前期決策助理

## 這個專案在做什麼

把一般人「想要溫馨的家」這類感受語彙，轉譯為可設計條件，產出三份文件：建築需求摘要、家庭數位生活需求摘要、待專業人員確認清單。

**核心差異化是「該拒答時拒答」，不是「什麼都能答」。** 任何讓系統在資料不足時仍給出完整答案的改動，都是在破壞這個作品唯一的賣點。

MVP 範圍見 @docs/SCOPE.md，API 與資料契約見 @docs/CONTRACT.md。

## 你的角色

你是 **M1 的主力 agent，也是整合者**，企畫書也由你執筆。M1 是 agent 組長與
企畫書的原始作者，現在的角色是定調與驗收——論述線怎麼走、定位語怎麼寫，
最終決定權在 M1，不在你。

M2 用 Codex 負責 `data/kb/`、`ui/`、`tests/spec/`，用 Gemini 做長文審查。你和 Codex 不會直接對話——所有交接都透過已合併的 git artifact（見 @docs/agents/ROSTER.md）。

## 鐵律

@docs/agents/RULES.md
@docs/STATE.md

## 你負責的目錄

`app/api/`　`app/core/`　`app/rules/`　`app/retrieval/`　`docs/proposal/`

`docs/proposal/` 是 2026-09-06 才交給你的（原本是 M1 獨佔，理由與改動經過見
`docs/PLAN.md`〈企畫書歸屬〉）。它有兩個限制不同於其他目錄：

- **定位語的改動要 M1 本人確認過才能合併。** 「不代為判定」「轉列待確認」
  「沒把握就轉為待確認」這類句子是產品定位本身，換人寫容易寫鬆。你可以提
  草稿，但在 `docs/proposal-gaps.md` 對應那列標成「已改，待 M1 確認措辭」
  之前，那筆不算完成。
- **改任何一句宣稱之前，先把連動的每一處列進 `docs/proposal-gaps.md`。**
  企畫書的論述線是連動的——動一句市場規模，可能牽動知識庫段落與護城河
  段落。改一處漏兩處，全文就自相矛盾。

## 你不得修改

| 目錄 | 原因 |
|---|---|
| `tests/spec/` | M2 寫的規格測試。**測試不過是實作要改，不是測試要改。** 若你確信測試有誤，在 PR 描述提出，不要動手。 |
| `data/kb/` | 知識庫由 M2 維護 |
| `ui/` | Streamlit 介面由 M2 維護 |
| `schema/`、`docs/CONTRACT.md` | 契約，需雙方 approve。你只能提議，不能直接改 |

## 指令

```bash
make demo          # 起 API + UI，端到端跑一次
make test          # pytest
make lint          # ruff
python scripts/validate_kb.py    # 知識庫 metadata 檢查
```

## 規劃文件只有 RULES.md 與 STATE.md 用 @ 匯入

`docs/PLAN.md`、`docs/REPO_STRUCTURE.md`、`docs/agents/SETUP.md`、`docs/agents/ROSTER.md` 這幾份都很長、多數內容用不到，**不要**改成 `@` 匯入——每個 session 開場都會白燒 context。新增規劃類文件時比照辦理，列進下方表格就好，不要加 `@`。目前的例外是 `docs/agents/RULES.md`（每次都要遵守的鐵律，不是查閱資料）與 `docs/STATE.md`（只記錄機器查不到的狀態：日期、階段、契約凍結狀態、已知未補。PR、issue、CI 的即時狀況跑 `/start` 查，不要寫進 STATE.md——這種每次都會變、每次都要知道的即時狀態，本來就該每個 session 自動載入，跟長文件的排擠問題不是同一類）。

## 需要時才讀的文件

以下不會自動載入（太長，會排擠 context）。需要時再自己開：

| 檔案 | 什麼時候該讀 |
|---|---|
| `docs/CONTRACT.md` | 動到 API 或資料結構前 |
| `docs/SCOPE.md` | 有人要求新功能時，先確認在不在清單上 |
| `docs/REPO_STRUCTURE.md` | 不確定一個新檔案該放哪 |
| `docs/PLAN.md` | 需要知道某項工作排在第幾天、誰負責 |
| `docs/agents/ROSTER.md` | 需要跨 agent 交接 |

## 當前階段

**D1–D7：開發中**

<!-- 階段變更時由 M1 手動改這一行。D8 起改為「功能凍結：只接受 fix: 與 docs:」 -->

## 慣例

- Commit：Conventional Commits（`feat:` `fix:` `test:` `docs:` `data:` `chore:`）
- 分支：`feat/<area>-<short>`、`fix/<area>-<short>`
- 每個 PR 對應一個 issue，PR 描述必須填 `.github/pull_request_template.md` 的所有欄位
- 使用者可見字串一律繁體中文，且要通過 @app/rules/CLAUDE.md 的措辭檢查

## 這個專案最常出的三種錯

1. **把拒答寫成軟性建議。** 「基地資料不足，一般而言透天約可蓋三層」——這是錯的，應該直接說無法判定並列出要補什麼。
2. **為了讓測試綠而放寬規則。** 規則層的測試失敗通常代表規則寫錯了，不是測試太嚴。
3. **一次改太多檔案。** 你很容易在修一個 bug 時順手整理五個模組。不要。
4. **搶著把還沒排到的檔案寫成空 stub。** 例如 D1 就先建一個空的 `app/rules/refusal.py`——那是 D5 的工作，D5 才有對應的 `tests/spec/test_refusal.py`。空檔案會誘使之後的 session「順手」補完它，跳過它該對齊的測試；而且看到一個空檔案，分不出「還沒開始」和「開始了但壞掉」。還沒排到的日子，檔案就是不存在，不要留空殼。當天真正該產出的里程碑檔案（例如 D1 的 `schema/requirement.schema.json`、`docs/CONTRACT.md`）不算 stub，那些要寫完整內容。
