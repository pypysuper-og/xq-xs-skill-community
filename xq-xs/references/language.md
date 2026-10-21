# 宣告、流程與序列

## 基本寫法

XS 使用不區分大小寫的關鍵字，以 `;` 結束敘述；`=` 在賦值與條件比較位置有不同角色。維持原程式的大小寫風格即可。不要把 Python 的縮排、`==` 或大括號區塊套過來。

```xs
Input: WindowSize(20, "期數");
Variable: MeanPrice(0), IsReady(false);

MeanPrice = Average(Close, WindowSize);
IsReady = CurrentBar > WindowSize;
if IsReady then begin
    if Close > MeanPrice then
        Ret = 1
    else
        Ret = 0;
end;
```

上例的 `Ret` 僅用於合適的警示／選股腳本，省略了完整參數與資料設定。`else` 前不能先用分號結束對應的 `if`。多個敘述用 `begin ... end`；`{ ... }` 與 `//` 為註解。關鍵字可經隨附查找工具搜尋，來源為 [流程控制目錄](https://xshelp.xq.com.tw/XSHelp/lists?a=CONTROLFLOW)。

## 一般參數與函數參數

一般腳本的 `Input` 指定預設值，例如 `WindowSize(20)`；函數腳本通常指定 `NumericSeries`、`NumericSimple`、`TrueFalseSeries` 或字串等型別。參數的預設值、顯示名稱與型別各有用途，不能混用。詳見 [Input](https://xshelp.xq.com.tw/XSHelp/?HelpName=Input&group=DECLARATION) 及 [宣告目錄](https://xshelp.xq.com.tw/XSHelp/lists?a=DECLARATION)。

`Variable`／`Var` 的初值決定數值、布林或字串型別。`Value1` 等內建暫存名稱存在，但自訂名稱通常較便於查錯。避免以內建欄位名遮蔽原本想讀取的行情資料。

## 迴圈與邊界

```xs
Variable: IndexNo(0), PositiveBars(0);
PositiveBars = 0;
for IndexNo = 1 to 5 begin
    if Close[IndexNo] > Open[IndexNo] then
        PositiveBars = PositiveBars + 1;
end;
```

這段片段需要至少五根可引用歷史資料。檢查迴圈起訖、`downto` 方向與計數器是否會終止；適合用 `TrueCount`、`Highest` 等官方函數表達時，先確認其視窗與回傳語義再使用。

## 中括號不是同一種操作

| 表達式 | 意義 |
|---|---|
| `Close[1]` | 主頻率前一根 bar 的收盤價 |
| `MyValue[1]` | 此變數在前一根主頻率 bar 的歷史值 |
| `GetField("月營收", "M")[1]` | 欄位自身月頻率的前一期資料，仍需考慮發布與對位 |
| `MyArray[1]` | 陣列元素；不是前一根 bar |

從 `[n]` 的擁有者判斷是時間位移還是元素索引。計算結果要讀過去值時，可先每根 bar 計算到具名變數，再引用變數的歷史值；不要任意為一般函數呼叫加 `[n]`，以免混淆其特殊語義與支援限制。跨頻率差異見 [data-and-time.md](data-and-time.md)。

## 交叉與持續狀態

`FastMA > SlowMA` 是狀態；`FastMA crosses over SlowMA` 是交叉條件。交叉的相等值處理與向前搜尋不能隨意簡化成一個兩根 bar 的比較。需要完全重現時核對 [CrossOver 官方實作](https://github.com/sysjust-xq/XScript_Preset/blob/d15a4157ccb2c439b3633dec200808924a7f83a7/%E5%87%BD%E6%95%B8/%E9%82%8F%E8%BC%AF%E5%88%A4%E6%96%B7/CrossOver.xs)。同根 bar 反覆洗價時，交叉條件也不等於永久只觸發一次。

## 從其他語言移植

逐項列出來源腳本的資料、函數、狀態、輸出與下單 API。對每項找 XS 等價語義；沒有等價項就標明差異。不要以語法相似為由沿用來源語言的策略狀態、成交假設或保留字。
