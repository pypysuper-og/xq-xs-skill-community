# 自訂函數、陣列與執行狀態

## 函數契約

函數名稱、回傳型別與編輯器設定需一致。函數內以該名稱賦值回傳；`Ret` 是其他腳本情境的輸出，不是通用函數回傳方式。

| 參數家族 | 用途 |
|---|---|
| `NumericSimple`／`NumericSeries` | 數值或可引用前期的數值序列 |
| `TrueFalseSimple`／`TrueFalseSeries` | 布林輸入與序列 |
| `StringSimple`／`StringSeries` | 字串輸入與序列 |
| `NumericRef` 等 `Ref` 型別 | 經參數回傳或修改呼叫者數值 |
| `NumericArray`／`NumericArrayRef` 等 | 陣列輸入；需確認維度與是否回寫 |

使用前核對 [Input 的型別說明與連結](https://xshelp.xq.com.tw/XSHelp/?HelpName=Input&group=DECLARATION)。不要以 Python 傳值／傳參照的直覺猜測 XS 的輸出參數。參數個數、順序、回傳值和輸出變數各自核對；技術指標函數不一定只回傳一個指標值。

## simple／series 計算

`SetBarMode(0)` 由系統判斷；`1` 是 simple 計算；`2` 是 series 計算。這個設定描述函數計算相依性，不是讓策略切換逐筆洗價的開關。[SetBarMode](https://xshelp.xq.com.tw/XSHelp/?HelpName=SetBarMode&group=GENERALFUNC)

無前期相依的視窗計算和使用前期狀態的遞迴計算，不能只因公式看似相同就互換。重構 series 計算時確認其呼叫次數、每根 bar 的連續求值、初值與暖機。把原本每根 bar 計算的遞迴指標移入偶爾成立的條件區塊，可能改變結果；這需要以明確資料比對，而非只看編譯。

## 陣列

```xs
Array: Samples[5](0);
Array: DynamicSamples[](0);
Array_SetMaxIndex(DynamicSamples, 5);
Samples[1] = Close;
DynamicSamples[1] = Close;
```

依 [Array 說明](https://xshelp.xq.com.tw/XSHelp/?HelpName=Array&group=DECLARATION)，一般元素存取採 `1` 到宣告大小；不要套用 Python 的零起始迴圈。動態陣列須設定大小後才使用。每個陣列函數另查其索引與長度契約，不能由 `[n]` 推定是時間序列；多維度與容量上限也不應從舊稿寫死。

## 同根 bar 的狀態

一般變數的歷史序列與同根 bar 逐筆保留狀態，是兩種需求。需要讓計數器、去重鍵或讀 Tick 的游標跨洗價保存時，使用正確宣告的 `IntrabarPersist`，並定義何時重置。

例如 [ReadTicks](https://xshelp.xq.com.tw/XSHelp/?HelpName=ReadTicks&group=PRICERELFUNC) 要求持續保存讀取游標。跨交易日重置與多商品各自保存狀態仍須由當前需求決定；夜盤不能一律用日曆日期作日盤重置。

對「只觸發一次」先確認是每次啟動、每根 bar、每個交易日、每個商品還是每個訊號一次，再選擇 `Once`、bar／日期鍵或明確狀態。不要只加一個布林旗標便宣稱跨重啟或跨商品去重成立。

## 重構前後比較

需要驗證計算等價時，以相同商品、頻率、初值與資料範圍比對代表性 bar；涵蓋不足歷史、相等值與條件分支。若只有靜態推論，保留「尚未在 XQ 執行比對」的限制。
