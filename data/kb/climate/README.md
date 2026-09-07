# 臺南站 2026-08 氣候切片

對應 issue #26；七筆來自 M2 提供的 C-B0026-001.json，Gemini Gem 1 切片、Codex 對照原件核對欄位。尚未人工逐筆查證，狀態以 ../VERIFIED.md 為準。

## 原件追溯

- 資料集：https://opendata.cwa.gov.tw/dataset/all/C-B0026-001
- identifier：9d31c190-7ff5-4d72-a002-a1b2a3ab115b
- SHA256：ECFC8A1E7607A43A21DBF9B926E28234633B8AC2B662545EEF7A1FBFF85634EE
- 測站：臺南／467410；YearMonth：2026-08。
- sent：2026-09-06T13:35:04+08:00。
- M2 已保存完整原件；資料集會滾動更新，回查需核對同月份、測站與原件識別資訊。

## 日期口徑與限制

version_date 採本次來源檔發布／產製日期 2026-09-06，並非觀測值最後修訂日期。
依據為官方資料字典 V1.1 第 5 頁（印刷頁 -2-）對 sent 的「發布日期／產生 XML 時間」定義：
https://opendata.cwa.gov.tw/opendatadoc/CWB_Data_Dictionary_V1.1.pdf
該文件使用舊 cwbopendata 名稱，本批為 cwaopendata；沿用欄位語意屬 metadata 判讀，仍待人工確認。若驗收要求觀測值最後修訂日，本證據不足，不得據此宣稱通過。

content 保存統計定義與觀測紀錄兩個 JSON 片段，是文字內容，不是單一 JSON 文件。
GE01Days 是有門檻的降雨日數；Precipitation 的 mm 單位不得套用到日數。
本批為單月測站觀測，不代表全年氣候、基地微氣候或建築節能效果。

## 顯名聲明

提供機關／交通部中央氣象署 中央氣象署氣候觀測_逐月_多要素氣象資料

此開放資料依政府資料開放授權條款 (Open Government Data License) 進行公眾釋出，使用者於遵守本條款各項規定之前提下，得利用之。

- 政府資料開放授權條款：https://data.gov.tw/license
- 氣象資料開放平臺使用規範：https://opendata.cwa.gov.tw/about/rules

授權依使用者貼回的使用規範及附件整理。產品引用／匯出時仍須帶入顯名資訊；本資料提交不代表 UI 已實作授權顯示。
