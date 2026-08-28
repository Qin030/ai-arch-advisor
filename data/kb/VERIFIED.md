# 知識庫人工查證台帳

> **這個檔案只有人能寫。任何 agent 不得修改。**
>
> 查證狀態刻意不放進切片的 YAML metadata——如果寫成 `verified: true` 這種欄位，
> agent 就能自己填。而要驗證的正是 agent 可能捏造的東西。

## 查證方式

對每一筆切片：

1. 開啟 `source_url`
2. 用瀏覽器搜尋 `content` 的前 20 個字，確認頁面上真的有這段文字
3. 對照頁面標示的修正／發布日期，確認與 `version_date` 相符
4. 確認適用地區標示正確

四項全過才打勾。**有任何一項不確定就標 ❌ 並在備註寫原因**，不要打問號放著。

## 台帳

| 切片 ID | 類型 | URL 可開啟 | 內容逐字相符 | 版本日期相符 | 地區正確 | 查證人 | 日期 | 備註 |
|---|---|---|---|---|---|---|---|---|
| reg-tainan-001 | regulation | | | | | | | |
| reg-tainan-002 | regulation | | | | | | | |
| reg-tainan-003 | regulation | | | | | | | |
| reg-tainan-004 | regulation | | | | | | | |
| reg-tainan-005 | regulation | | | | | | | |
| reg-tainan-006 | regulation | | | | | | | |
| reg-tainan-007 | regulation | | | | | | | |
| reg-tainan-008 | regulation | | | | | | | |
| reg-tainan-009 | regulation | | | | | | | |
| reg-tainan-010 | regulation | | | | | | | |
| cost-tainan-001 | cost | | | | | | | |
| cost-tainan-002 | cost | | | | | | | |
| cost-tainan-003 | cost | | | | | | | |
| cost-tainan-004 | cost | | | | | | | |
| cost-tainan-005 | cost | | | | | | | |
| cost-tainan-006 | cost | | | | | | | |
| cost-tainan-007 | cost | | | | | | | |
| cost-tainan-008 | cost | | | | | | | |
| cli-tainan-001 | climate | | | | | | | |
| cli-tainan-002 | climate | | | | | | | |
| cli-tainan-003 | climate | | | | | | | |
| cli-tainan-004 | climate | | | | | | | |
| cli-tainan-005 | climate | | | | | | | |
| cli-tainan-006 | climate | | | | | | | |
| cli-tainan-007 | climate | | | | | | | |

## 抽查紀錄

D4 的 `/kbaudit` 至少抽 30%（8 筆）人工核對。D10 稽核前全部 25 筆都要打完勾。

| 日期 | 抽查筆數 | 發現問題 | 處理 |
|---|---|---|---|
| | | | |

## 發現捏造時

**停止所有開發**，25 筆全部重查。這是規劃書裡唯一一條「違反即停工」的規則——
企畫書的整個立論建立在「每筆資料可追溯來源、版本與適用地區」，
一筆捏造的切片就足以讓評審在 Q&A 拆掉整個作品。
