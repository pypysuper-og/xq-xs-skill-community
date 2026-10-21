# 原創 XS 範例

以下是便於修改的獨立範例，未從官方 preset 複製程式本體。**均未在 XQ 編譯或執行**；使用時先在對應類型編譯，核對商品、資料與頻率。它們展示程式形狀，不提供獲利或實盤驗證。

| 檔案 | XQ 類型／名稱 | 示範 |
|---|---|---|
| [ma-indicator.xs](../assets/examples/ma-indicator.xs) | 指標 | 兩條移動平均線與輸入範圍 |
| [ma-screen.xs](../assets/examples/ma-screen.xs) | 選股 | 均線交叉與命名輸出欄位 |
| [ma-alert.xs](../assets/examples/ma-alert.xs) | 警示 | 交叉條件；不額外保證通知去重 |
| [XSChangePercent.xs](../assets/examples/XSChangePercent.xs) | 數值函數，命名為 `XSChangePercent` | 具型別輸入及明確的零分母錯誤 |
| [XSAboveThreshold.xs](../assets/examples/XSAboveThreshold.xs) | 布林函數，命名為 `XSAboveThreshold` | `function_bool` 與真假回傳 |
| [ma-autotrade-disabled.xs](../assets/examples/ma-autotrade-disabled.xs) | 自動交易 | 多單範例、退出優先、集中一次交易指令 |

## 共同假設

均線範例用原始 `Close`，以固定 300 筆讀取／引用設定搭配 1–250 的整數期數範圍，讓示範界線容易檢視；不是所有策略的通用設定。使用者需要更長期數、跨頻率或還原資料時，重新配置，不只放寬參數檢查。

範例的「5／20」是五／二十根 bar，不自動代表日。選股應在支援的日或更長頻率使用；沒有在檔案內替使用者決定還原方式或市場。歷史不足時 `CurrentBar` 的條件只是局部防護，仍需核對實際資料。

交叉使用 XS 的正式 `crosses over`／`crosses under`。需要改成持續高於均線，或完成 bar 才發訊號時，先明確改變契約，不把兩種行為混在一起。

## 函數匯入

在 XQ 編輯器建立正確回傳型別與名稱，再貼入函數程式；函數內的回傳賦值名稱需完全對應。數值函數對零分母採執行錯誤，是本範例的選擇，並非所有指標的必然規則。

## 交易範例的界線

`EnableOrders` 預設 `false`，因此預設不呼叫交易指令。若在 XQ 將它設為 `true`，程式便具有送單路徑；請僅在已授權、設定清楚的環境修改與驗證。

它只示範多單交叉與反向交叉退出，使用 `Close` 指定限價；不保證成交。退出可涵蓋尚未成交或部分成交的進場，並避免在待平倉時把 `Position = 0` 單獨當成重新進場條件。範例沒有停損、停利、超時追價、交易時段退出、帳戶同步或完整故障恢復；不適合作為已就緒實盤策略。

查官方相近範例時使用 `lookup.py --source preset`，直接開啟固定 commit 連結。不要把這些原創骨架誤稱為官方已編譯範例。
