# 資料欄位、頻率與時間

## 選對資料來源

| API／命名空間 | 用途 | 必須確認 |
|---|---|---|
| `GetField` 資料欄位 | 指標、警示與交易的資料序列 | 商品、頻率、單位與歷史可用性 |
| `GetField` 選股欄位 | 選股環境的基本面、價量與籌碼 | 同名欄位在選股情境的支援 |
| `GetQuote`／`q_...` | 警示、交易中的最新報價 | 沒有可供回測的前期報價序列 |
| `GetSymbolField` | 明確指定其他商品的欄位 | 商品代碼、對位、交易時段 |
| `GetSymbolInfo` | 商品屬性 | 這是屬性還是有歷史期別的欄位 |

在離線索引中，`quote`、`data`、`selection` 分開存放；同名「收盤價」不能去重成一個通用欄位。正式支援範圍以 [GetField](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetField&group=FIELDFUNC)、[GetQuote](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetQuote&group=FIELDFUNC) 與個別欄位頁為準。

## 缺值不等於不支援

`GetField` 省略頻率時使用執行頻率。對月營收或季度財報等有明確期別的欄位，應明示需要的頻率，不讓主圖切換偷偷改變資料語義。

`Adjusted:=true` 與 `Default:=...` 是具名參數。預設值可以處理對應 K 棒缺資料的情形，不能遮蔽不支援的商品／欄位／頻率，也不能使未來索引合法。若零本身是合法財務數據，將缺值填零可能直接改變選股結果；先決定缺值應排除、另標記或採其他策略。[GetField 參數說明](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetField&group=FIELDFUNC)

需要能力檢查時查 `IsSupportField`、`CheckField` 的當前簽章；不要從名稱猜參數。對發布時間敏感的資料，分別查 `GetFieldDate` 與 `GetFieldPublishDate`，確認資料期別和當時已公布的時間。

2026-11-09 另核對：[`IsSupportField`](https://xshelp.xq.com.tw/XSHelp/?HelpName=IsSupportField&group=FIELDFUNC) 判斷欄位／頻率支援，True 不保證當棒有值；[`CheckField`](https://xshelp.xq.com.tw/XSHelp/?HelpName=CheckField&group=FIELDFUNC) 的公開呼叫形式是欄位、頻率兩個參數，不能從說明文字自行補出第三個商品參數。跨商品檢查需另查對應 API。

[`GetFieldPublishDate`](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetFieldPublishDate&group=FIELDFUNC) 取得欄位在 XQ 更新的 YYYYMMDD 日期，並支援欄位前 N 期的更新日；它不是公司的精確公告時刻。

## 對位、版本與資料權限

[`SetAlign`](https://xshelp.xq.com.tw/XSHelp/?HelpName=SetAlign&group=GENERALFUNC) 現行頁以 0 表示所屬期別對位、1 表示 XS 可取得資料的公布日對位。頁面列指標預設 0，警示／交易預設 1；選股不支援此函數。歷史研究需明確核對設定、資料修訂與目標版本，不以對位設定本身保證沒有未來資訊。

[跨腳本支援選股欄位的官方教學](https://www.xq.com.tw/lesson/xspractice/xs%E6%8C%87%E6%A8%99-%E7%AD%96%E7%95%A5%E9%9B%B7%E9%81%94-%E8%87%AA%E5%8B%95%E4%BA%A4%E6%98%93%EF%BC%9A%E6%94%AF%E6%8F%B4%E9%81%B8%E8%82%A1%E6%AC%84%E4%BD%8D/) 說明 15.01 後，具相應權限時可在指標／雷達／交易使用選股欄位。不能僅憑「選股欄位」分類全面准許或禁止；仍需看個別欄位、F7、資料權限與版本。該教學對警示／交易預設對位的舊敘述與現行 SetAlign 頁有差異，需保留差異並核對目標環境。

## 欄位位移與變數位移

日線腳本內先把月營收存進變數，再用變數 `[1]`，取得的是前一個日線運算留下的值，可能仍是同一個月營收。要比較不同月期，使用欄位自身的位移，再存成兩個變數：

```xs
Variable: LatestRevenue(0), PriorRevenue(0);
LatestRevenue = GetField("月營收", "M");
PriorRevenue = GetField("月營收", "M")[1];
```

以上只示範位移位置，並未證明資料當時已公布。官方的 [欄位對位說明](https://www.xq.com.tw/lesson/xspractice/%E5%8F%96%E5%BE%97%E8%B3%87%E6%96%99%E6%AC%84%E4%BD%8D%E6%99%82%E7%9A%84%E3%80%8C%E5%B0%8D%E4%BD%8D%E5%95%8F%E9%A1%8C%E3%80%8D/) 特別說明這個差異。

## 主頻率、跨頻率與歷史資料

- `CurrentBar` 是目前運算的主頻率 bar 編號，不是交易所的全歷史資料總數。
- `SetTotalBar` 控制腳本執行前讀取與運算的資料範圍；`SetBackBar` 控制指定頻率最大引用筆數。兩者不互相取代，也不能保證新上市商品真的有足夠資料。[SetTotalBar](https://xshelp.xq.com.tw/XSHelp/?HelpName=SetTotalBar&group=GENERALFUNC)、[SetBackBar](https://xshelp.xq.com.tw/XSHelp/?HelpName=SetBackBar&group=GENERALFUNC)
- 跨頻率每個序列分別確認引用範圍。分鐘腳本讀取日／週值時，該日／週可能尚未結束；不要假設讀到的都是完成期別。
- `xf_`／`xfMin_` 系列並非所有腳本通用。例如 [xfMin_CrossOver](https://github.com/sysjust-xq/XScript_Preset/blob/d15a4157ccb2c439b3633dec200808924a7f83a7/%E5%87%BD%E6%95%B8/%E8%B7%A8%E9%A0%BB%E7%8E%87/xfMin_CrossOver.xs) 明示選股限制。先查實際函數與版本。
- 本次核對的 [xfMin_EMA 固定原始碼](https://github.com/sysjust-xq/XScript_Preset/blob/d15a4157ccb2c439b3633dec200808924a7f83a7/%E5%87%BD%E6%95%B8/%E8%B7%A8%E9%A0%BB%E7%8E%87/xfMin_EMA.xs) 已列 2、3、20 分鐘，但 [個別說明頁](https://xshelp.xq.com.tw/XSHelp/?HelpName=xfMin_EMA&group=FREQUENCYFUNC) 的清單仍未列這幾項。依目標環境的系統函數版本查證；不能由一個版本推論所有頻率或所有 xfMin 函數都通用。
- `Date`／`Time` 所屬 bar 的時間和 `CurrentDate`／`CurrentTime` 的現行時間不同；回測中不要以電腦現在日期冒充歷史時點。

## Tick 與單位

一次洗價不一定對應一筆交易所成交。需要逐筆重建時查 `ReadTicks`、Tick 序號與 MultiTick 說明，不用洗價次數代替成交次數。[ReadTicks](https://xshelp.xq.com.tw/XSHelp/?HelpName=ReadTicks&group=PRICERELFUNC)

每個欄位分別查單位：成交量可能是張、股或口；百分比常以 `5` 表示 `5%`，並非 `0.05`；金額可能以元、千元或億元表示。不同市場與商品不可直接共用換算常數。

## 回測最容易漏掉的證據

資料期別、實際發布日、還原方式、主頻率、跨頻率對位、歷史缺值及當時商品母體，都可能改變結果。先在少量明確日期輸出原始欄位、資料日期與條件值，核對後再擴大期間。即時資料無法取得歷史版本時，明示該段回測未被驗證。
