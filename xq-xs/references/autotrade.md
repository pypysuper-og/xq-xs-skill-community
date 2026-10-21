# 部位、委託與成交

## 三個不同狀態

| 名稱 | 所代表的狀態 | 不能據此宣稱 |
|---|---|---|
| `Position` | 目前商品的策略預期部位 | 券商已成交或帳戶總庫存 |
| `Filled` | 目前商品的策略成交部位，可反映部分成交 | 所有委託都已完成或已無風險 |
| 券商帳戶庫存 | 帳戶實際持有；受啟動部位等設定影響 | 必然等於任一策略的相對部位 |

每個商品獨立計算。先確認策略啟動部位與使用者意圖，再寫數量；不可為了配合範例，擅自把既有部位視為零。[Position](https://xshelp.xq.com.tw/XSHelp/?HelpName=Position&group=TRANSACTIONFUNC)、[Filled](https://xshelp.xq.com.tw/XSHelp/?HelpName=Filled&group=TRANSACTIONFUNC)

`SetPosition(2)` 指定目標為多單兩個單位，不是每次都再買兩個單位；`SetPosition(0)` 要達到策略空手，也不代表呼叫當下已平倉。數量單位依市場／商品確認。[SetPosition](https://xshelp.xq.com.tw/XSHelp/?HelpName=SetPosition&group=TRANSACTIONFUNC)

## 一次洗價內的先後順序

目前官方文件與 [部位異動時機範例](https://github.com/sysjust-xq/XScript_Preset/blob/d15a4157ccb2c439b3633dec200808924a7f83a7/%E8%87%AA%E5%8B%95%E4%BA%A4%E6%98%93/0-%E5%9F%BA%E6%9C%AC%E8%AA%9E%E6%B3%95/07-Position%E8%B7%9FFilled%E7%9A%84%E7%95%B0%E5%8B%95%E6%99%82%E6%A9%9F%E9%BB%9E.xs) 確認：

1. 洗價前決定 `Position` 與 `Filled` 的快照。
2. 這次執行期間，兩個值維持不變。
3. 該次僅採用第一個交易指令，後續交易指令會被忽略。
4. 執行結束後再依指令處理委託；後續洗價才看到更新的部位／成交狀態。

因此多個獨立 `if` 不等於最後一個目標覆蓋前面的目標。可先依使用者要求的優先序決定「這次是否下指令、目標部位、價格」，最後集中呼叫一次；不要為了集中而每次洗價無條件重送。

## 待成交與退出

| 情境 | 審查重點 |
|---|---|
| `Position > 0`、`Filled = 0` | 可能有待成交買單；條件失效後是否取消／改目標？ |
| `Position > Filled > 0` | 已部分成交；退出不能等到全部成交才准處理 |
| `Position = 0`、`Filled > 0` | 可能正等待平倉；不能立即當成空手再進場 |
| `Position = Filled` | 部位與預期一致；不等於帳戶、風控或外部連線已被驗證 |

`Position = Filled` 可用於某些新進場或加碼條件，不能一律包住停損、取消與退出。針對實際策略明確測試未成交、部分成交和條件失效。

刪除委託與平掉已成交部位是不同目的。查 [CancelAllOrders](https://xshelp.xq.com.tw/XSHelp/?HelpName=CancelAllOrders&group=TRANSACTIONFUNC) 及其官方教學，不把刪單當成平倉完成，也不從成功呼叫直接推論結果。

## 價格與執行選擇

省略價格時由策略預設買／賣價格設定決定；`Close` 是指定價格的運算值，並非必然成交價。`MARKET` 依市場與帳戶類型有相應處理，不能概括成無條件保證成交。需要跳動檔位時查 `AddSpread`，不要把固定價格差誤稱為一檔。[SetPosition 價格參數](https://xshelp.xq.com.tw/XSHelp/?HelpName=SetPosition&group=TRANSACTIONFUNC)

同目標再次呼叫可能涉及改價。檢查是否因每次洗價、`Position + 1`、雙重分支或停損優先序而重複加碼／改單。重啟、斷線與帳戶同步另看實際平台證據，不自行重播結果未知的交易操作。

## 交付時說清楚

只列當前策略實際需要的事項：多空與反手、最大部位、價格、退出、待成交處理、交易時段、費用與滑價假設。未實作的風控明示，不額外替使用者選交易風險。範例預設關閉交易指令，見 [examples.md](examples.md)。

本 skill 的程式撰寫、靜態審查與包裝不會登入 XQ、啟動策略或發送交易。實盤操作及其驗證仍須有該操作的明確授權。
