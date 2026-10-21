# 腳本類型與輸出

## 選擇入口

| 用途 | 官方匯出註解慣例 | 結果／限制 |
|---|---|---|
| 指標 | `{@type:indicator}` | `Plot1` 等繪圖；不能當交易腳本送單 |
| 警示／策略雷達 | `{@type:sensor}` | `Ret = 1` 表示條件符合；警示本身不等於成交 |
| 選股 | `{@type:filter}` | `Ret` 決定是否入選，`OutputField` 加輸出欄位 |
| 自動交易 | `{@type:autotrade}` | 交易指令設定策略預期部位，另看成交狀態 |
| 數值函數 | `{@type:function}` | 具型別的 `Input`，賦值給函數名稱回傳數值 |
| 布林函數 | `{@type:function_bool}` | 具型別的 `Input`，賦值給函數名稱回傳真假 |

這些註解出現在官方 `.xs` 原始檔；建立腳本時仍需在 XQ 選擇正確類型／函數回傳設定。第一行註解不是已編譯、已匯入或 API 支援的證據。不要僅從註解推論 runtime 如何處理檔案。

數值型別有 [Average.xs](https://github.com/sysjust-xq/XScript_Preset/blob/d15a4157ccb2c439b3633dec200808924a7f83a7/%E5%87%BD%E6%95%B8/%E5%83%B9%E6%A0%BC%E8%A8%88%E7%AE%97/Average.xs) 的 `function` 實例，布林型別有 [CrossOver.xs](https://github.com/sysjust-xq/XScript_Preset/blob/d15a4157ccb2c439b3633dec200808924a7f83a7/%E5%87%BD%E6%95%B8/%E9%82%8F%E8%BC%AF%E5%88%A4%E6%96%B7/CrossOver.xs) 的 `function_bool` 實例。這不構成所有可能匯出型別的完整清單；其他回傳型別要依編輯器及同型別官方檔案確認，不自行發明 `function_num` 等別名。

## 容易混淆的邊界

- `Ret` 的選股／警示用途與函數回傳值不同。自訂函數須以腳本的實際函數名稱賦值。
- 同名 `GetField` 會依執行情境使用資料欄位或選股欄位，支援頻率與商品不能互相套用。
- 選股不支援 Tick／分鐘頻率。盤中逐筆條件通常需要警示或交易腳本；不能只把標頭改成 `filter`。[GetField 說明](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetField&group=FIELDFUNC)
- 自訂函數不能替呼叫者解除 API 限制。讀取報價或呼叫交易功能，仍須查該 API 與呼叫情境。
- 同一策略的不同商品各有獨立部位；跨商品資料查詢也不會自動建立共享持倉狀態。

## 選型時的最小確認

先問結果要畫圖、入選、通知、回傳數值，還是改變部位。只有要寫進出場程式時，才進一步確認數量、價格、成交與風控。若只是審查，保留原有腳本類型與交易意圖。

完整範例與匯入名稱見 [examples.md](examples.md)，資料與交易細節分別見 [data-and-time.md](data-and-time.md)、[autotrade.md](autotrade.md)。
