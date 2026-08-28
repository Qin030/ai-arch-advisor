---
description: 依契約產出功能規格，不寫任何程式碼
---

為 $ARGUMENTS 產出實作規格。

**這個指令不寫程式碼。** 只產出規格文件，供 M2 的 Codex 據以撰寫測試。

步驟：

1. 讀 `docs/CONTRACT.md` 與 `schema/requirement.schema.json`
2. 若涉及拒答邏輯，讀 `app/rules/CLAUDE.md` 的六個必測情境
3. 產出規格，必須包含：
   - 輸入：欄位、型別、必填與否
   - 輸出：成功情況的完整結構
   - **拒答情況**：觸發條件、`missing_field`、`confirm_with`、`impact`、`reason`
   - 邊界情況：至少三個
   - 明確排除：這個功能「不做」什麼
4. 寫入 `docs/specs/<name>.md`，開 PR

**規格裡不要出現函式名稱、類別名稱或檔案路徑。** 規格描述行為，不描述實作——否則 M2 寫測試時會被你的實作決策綁死。

若契約不足以寫出規格 → 列出缺什麼，停下來問 M1。
