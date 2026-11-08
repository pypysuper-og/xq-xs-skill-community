# SDT 資料表與 Group 商品清單

需要保存表格狀態、同策略跨商品共享，或遍歷商品清單時讀本頁。2026-11-09 核對官方文件；本頁不是 XQ 執行證據。

## 先選資料的作用範圍

依 [官方 SDT 教學](https://www.xq.com.tw/lesson/xspractice/sdt-sharedatatable/)，無後綴的 SDT 函數使用每個執行商品各自的表；`_L` 使用同一策略內商品共享的表。`_L` 限即時策略雷達／自動交易，不能直接套到指標、選股或各種回測，也不能當成跨策略共享。

SDT 只保存目前狀態，不能把 `[n]` 當成前期表格快照。若需要歷史狀態，先明確設計保存方式，再驗證生命週期。

## 讀寫與排序

| 工作 | 已核對的介面與注意點 |
|---|---|
| 讀數值 | `SDT_GetValue(key, column, default:=0)`；key 是字串，column 可為序號或名稱。找不到 key／column 才採 default；現存字串轉換失敗則為 0，不能把它當成同一種缺值。[官方頁](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_GetValue&group=SDTFUNC) |
| 條件更新共享值 | `SDT_SetValueIf_L(key, column, newvalue, oldvalue)` 回傳布林。檢查成功結果；不要顛倒新舊值參數。[官方頁](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SetValueIf_L&group=SDTFUNC) |
| 取得 keys | `SDT_GetKeys(output_key_array)` 寫入一維字串陣列，不保證取回順序。[官方頁](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_GetKeys&group=SDTFUNC) |
| 按數值排序 | `SDT_Sort(column, sorted_key_array, order:=-1)`；-1 小到大、1 大到小，輸出為 key 陣列。[官方頁](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Sort&group=SDTFUNC) |

[現行 SDT 清單](https://xshelp.xq.com.tw/XSHelp/lists?a=SDTFUNC) 本次可見 38 個名稱。查其他函數時使用 `lookup.py --source supplement`，開啟個別說明，不從命名規律推測未查證的參數或回傳值。

## 多商品更新與生命週期

官方教學只保證單次 SDT 呼叫安全，多次呼叫之間可能有別的商品更新資料。因此「先算總額、判斷後各自寫入」不能直接證明嚴格的全策略資金上限；這是依並行條件作出的審查推論。條件寫入也不代表多個欄位一起更新成一筆交易。

CSV 初始化屬自動交易中心的策略表功能，不能當成所有腳本通用的即時持久化資料庫。空表、缺 key 的初始化、型別轉換與重啟恢復，應依實際使用情境補證據。[作用範圍與 CSV 說明](https://www.xq.com.tw/lesson/xspractice/sdt-sharedatatable/)

## Group 是商品清單

[`Group`](https://xshelp.xq.com.tw/XSHelp/?HelpName=Group&group=DECLARATION) 是宣告語法。使用 `GetSymbolGroup` 取得商品相關清單：一個字串參數是清單種類；兩個字串參數依序為指定商品、清單種類。[GetSymbolGroup](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetSymbolGroup&group=GENERALFUNC)

先用 [`GroupSize`](https://xshelp.xq.com.tw/XSHelp/?HelpName=GroupSize&group=GENERALFUNC) 檢查數量，避免空清單或索引超界。函數接收清單的形式可見 `Input: Members(Group);`，不能改成一般數值輸入。清單是否存在與商品是否支援須逐項確認。

Group 用來取得成員，SDT 用來保存狀態，[Rank](screening-and-alerts.md) 用來排行；依需求選擇，不能只替換名稱就視為相同計算。
