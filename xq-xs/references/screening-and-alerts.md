# 選股、排行與警示

## 選股結果

選股腳本以 `Ret = 1` 表示符合條件。可明確在當次判斷前設定 `Ret = 0`，讓輸出與條件的關係容易檢查。用 `OutputField(序號, 數值, 小數位數, 名稱)` 加上供核對的結果欄位。

`OutputField1` 等編號形式與 `SetOutputName` 也有官方說明；新範例使用帶序號與名稱的形式，便於集中閱讀。不應把現有有效的編號形式誤判為不存在。[OutputField](https://xshelp.xq.com.tw/XSHelp/?HelpName=OutputField&group=GENERALFUNC)

在少量指定商品、日期上輸出原始欄位與中間條件，通常比直接對大範圍選股結果猜原因更有用。暫時用 `Ret = 1` 檢視所有商品時，須說明它是除錯變更，不能當成策略原結果。

## 排行不是一般函數區塊

`Rank` 只適用選股。每個物件在頂層宣告，不能巢狀放進一般 `if`；區塊內以 `retval` 提供排序依據。物件內有自己的參數／變數範圍，不直接引用外部 `Input`；需要參數化時查當前正式支援寫法。[官方排行教學](https://www.xq.com.tw/lesson/xspractice/%E6%8E%92%E8%A1%8C%E8%AA%9E%E6%B3%95/)

例如只示範固定十期乖離排行的形狀：

```xs
Rank BiasOrder desc begin
    retval = Close - Average(Close, 10);
end;
```

這不是完整選股策略。`pos`、`range`、`pr` 的方向與尺度不同；`pos` 越小排名越前，`pr` 的方向相反。查核母體與有效性，不能把未參與排行的商品當成前幾名。`IsValid`、四分位等較新屬性要核對使用者版本。[Rank](https://xshelp.xq.com.tw/XSHelp/?HelpName=Rank&group=DECLARATION)

商品清單／群組與排行母體也需要明確。查 `Group`、`GetSymbolGroup`、`GroupSize` 時以現行文件為準；離線索引可能未涵蓋新增語法。

## 警示與洗價

警示的「條件為真」和「使用者收到一次通知」是兩項行為。確認平台的洗價與通知設定，以及腳本是否需要每根 bar、每次交叉或每個交易日一次。

`crosses over` 不是對通知次數的保證。若需要去重，選定可識別訊號的 bar／交易日鍵，用正確逐筆狀態並說明重置時機；見 [functions-and-state.md](functions-and-state.md)。不要把所有警示一律改成每天一次。

使用 `GetQuote` 時，保留其警示／交易限制及無歷史報價序列的特性。要支援回測，先確認是否存在語義相符的歷史欄位，不能只換 API 名稱便聲稱結果等價。[GetQuote](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetQuote&group=FIELDFUNC)

## 釐清頻率

日線選股不等於盤中逐筆監看；週線／月線資料也不一定已收完該期。先界定是當期變動值、前一完成期，還是前一公布期，再決定欄位與位移。原創範例見 [examples.md](examples.md)。
