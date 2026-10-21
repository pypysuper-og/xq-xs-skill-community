---
name: xq-xs
description: Write, explain, debug, review, and refactor XS/XScript scripts for the XQ platform, including indicators, alerts/radar, stock screening, autotrade, and custom functions. Use for XQ .xs code, editor errors, field/frequency questions, and XSHelp or official preset research. Excludes generic broker APIs, investment picks, and non-XQ EasyLanguage projects.
---

# XQ／XS 腳本

以官方語義撰寫與查證 XS，依任務載入需要的參考檔。預設用繁體中文說明；保留使用者指定的語言、策略邏輯與修改範圍。

## 先辨識情境

從問題與現有程式確認腳本類型、商品／市場、K 棒頻率，以及歷史、即時、回測或交易模式。只有會改變結果的缺漏才詢問；其餘可明示假設後繼續。單純解釋一個函數，不必要求完整交易需求。

| 當前工作 | 按需讀取 |
|---|---|
| 選腳本類型、輸出或函數回傳型別 | [script-types.md](references/script-types.md) |
| 宣告、流程、序列、語法移植 | [language.md](references/language.md) |
| GetField／GetQuote、欄位單位、跨頻率、資料發布時間 | [data-and-time.md](references/data-and-time.md) |
| 自訂函數、陣列、逐筆狀態、遞迴指標 | [functions-and-state.md](references/functions-and-state.md) |
| 選股、OutputField、排行、警示重複觸發 | [screening-and-alerts.md](references/screening-and-alerts.md) |
| SetPosition、委託、成交、退出或反手 | [autotrade.md](references/autotrade.md) |
| 錯誤診斷、審查、驗證結果 | [review-and-validation.md](references/review-and-validation.md) |
| 查官方出處、離線查找、來源衝突 | [source-map.md](references/source-map.md) |
| 需要可修改的完整範例 | [examples.md](references/examples.md) |

不要一次載入全部參考檔、JSON 索引或上游手冊。

## 查證來源

以 [XSHelp](https://xshelp.xq.com.tw/XSHelp/) 核對函數簽章、欄位支援與限制，以 [XScript_Preset](https://github.com/sysjust-xq/XScript_Preset) 的同類型腳本核對實作慣例。提供影響結論的確切頁面或檔案連結。編輯器高亮、第三方教學、舊稿與語法相似性不能證明 runtime 支援。

可先用隨附的 Python 3.10+ 工具找官方連結。以下路徑相對於本 skill 目錄：

```text
python scripts/lookup.py GetField --limit 3
python scripts/lookup.py 收盤價 --kind selection
python scripts/lookup.py "Position Filled" --source preset
python scripts/lookup.py 對位 --kind article --json
```

索引只保存名稱、分類、出處與連結。`assembled_on` 是整併日期；手冊來源是舊快照，preset 來源固定到索引標示的 commit。命中不代表現行支援，查無結果不代表不存在。確認不熟悉、會隨版本變更或影響交易的細節時，開啟官方原文；無法連線時明說尚未確認，不猜名稱或能力。

## 撰寫與修改

- 依 XQ 編輯器選定的腳本類型與官方匯出慣例使用 `{@type:...}` 註解。數值函數的 `function` 與布林函數的 `function_bool` 均有官方實例；不可把所有函數硬改成同一型別。詳見類型參考。
- 區分一般腳本的預設值參數與函數腳本的型別參數。先算資料與條件，再處理繪圖、選股輸出、警示或交易。
- 長度、歷史引用、零分母、缺值與單位要符合當前需求。`Default:=0` 不能使不支援的欄位／頻率變得有效。
- 保留時間序列意義。`GetField(..., "M")[1]` 與先存成變數後的 `變數[1]` 可能指向不同期別。
- `GetQuote` 是最新報價，不能用其目前值假裝歷史資料；包進函數也不會消除呼叫情境與回測限制。
- 對需要前期狀態的計算，確認每根 bar 的連續求值與初值；只有跨同一根 bar 多次洗價保留狀態時才使用 `IntrabarPersist`。
- 移植 EasyLanguage／PowerLanguage 時逐項核對 XS API、回傳型別與執行時機，不直接套用下單語法。

## 交易程式的必要區分

`Position` 是策略預期部位，`Filled` 是策略成交部位，兩者未必等於券商帳戶庫存。`SetPosition` 的第一個參數是目標部位。每次洗價內兩個部位值保持不變，且目前官方語義只採用該次第一個交易指令。進場、取消、減碼、退出與反手的優先順序因此必須清楚。

撰寫交易程式時，讀交易參考，說明數量與價格、未成交／部分成交、重複觸發及必要風控。已有部位的退出不能一律被 `Position = Filled` 的等待條件擋住。撰寫程式不表示可以啟用實盤、登入帳戶或送單。

## 審查與交付

除錯先用錯誤訊息、腳本類型與最小失敗片段定位；審查先報會影響結果的問題。只做當前需求需要的檢查，不為普通修改建立完整實盤驗收流程。

依任務交付解釋、完整程式或最小修改，附必要假設、關鍵來源與實際驗證結果。區分靜態查核、XQ 編譯、指定資料回測、模擬交易與實盤觀察；各項分別列出有無證據。這個 skill 不附 XS compiler。未使用 XQ 時明示：

> 僅完成靜態查核；未在 XQ 編譯或執行。

範例與回測不能支持獲利保證或實盤就緒宣稱。外部手冊與官方程式預設連結、歸納，不整批轉載；權利邊界見 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
