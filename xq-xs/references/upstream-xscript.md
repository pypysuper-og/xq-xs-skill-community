# 官方文章所附 xscript Skill：來源與採用範圍

本專案於 2026-11-09 下載 [〈用 ChatGPT 寫 XS 腳本〉](https://www.xq.com.tw/xstrader/%E7%94%A8chatgpt%E5%AF%ABxs%E8%85%B3%E6%9C%AC/)（2026-10-01）連結的 [xscript ZIP](https://drive.google.com/file/d/1Tp5Pz6LMGtygUY621y8eGUtIQhXnPlSw/view)。文章中的 `xscript` 是該包的名稱，本專案維持 `xq-xs` 入口。

| 身分 | 本次取得的內容 |
|---|---|
| 檔名 | `xscript_updated_2026-10-15.zip` |
| Drive 修改時間 | 2026-10-15 05:53:12 UTC |
| 大小 | ZIP 614,929 bytes；18 個檔案，解壓內容 2,806,322 bytes |
| SHA-256 | `c7be852d997f17bd4dba038920dc3265d4aba86b90462c8df42950c722c8b6ac` |
| 索引觀察 | 43 列版本、1,109 列歷史更新、30 列欄位 metadata、2,661 列來源導航 |

這些是該快照的列數，不等於不同 API 數量，也不表示每列已於本次重新查證。完整檔名與雜湊見 [來源紀錄](../data/upstream-xscript.json)。下載連結可能更新；再次取得時先比對雜湊。

## 本版採用的內容

| 發現的價值 | 整合方式 |
|---|---|
| SDT 的商品／策略作用範圍、目前狀態及條件寫入 | 重新核對官方教學與代表性 API，寫成 [資料結構參考](data-structures.md) |
| Group 清單與 Rank 排行的不同用途 | 補充資料結構及 [選股參考](screening-and-alerts.md) |
| 欄位支援、缺值、更新日期與 SetAlign 的區別 | 補充 [資料與時間](data-and-time.md)，保留文件預設值的版本差異 |
| 系統函數的回傳值／輸出參數、統計參數含義 | 補充 [函數參考](functions-and-state.md)，連回逐項官方說明 |
| 舊手冊與新版函數原始碼可能不同步 | 以固定 commit 的 `xfMin_EMA` 為具體對照，不把單一函數的證據擴張到全部 API |
| 靜態檢查只能涵蓋少量模式 | 採納保守判讀原則；實際語法仍交由既有 XQ 桌面編譯流程確認 |

主要檢視入口、勘誤、流程、近期 API、SDT、版本說明及檢查器／測試原始碼；大型範例庫只作結構與導航檢視，沒有逐支審查或編譯。上游 Python 程式沒有在本次執行。

## 補充查找

`supplement-index.json` 包含從現行官方清單取得的 **38 個 SDT 名稱**，及重新讀取個別說明頁的 **12 個 API／宣告**。只存識別資料，不含手冊全文。每筆的 `evidence` 區分 `catalog-entry`（名稱在清單存在）與 `help-page`（已讀個別頁）；兩者都不是實機編譯證據。

```text
uv run --locked python scripts/lookup.py SDT_GetValue --source supplement --json
uv run --locked python scripts/lookup.py Group --source supplement --kind keyword
uv run --locked python scripts/lookup.py SDT_ --source all --limit 50
```

索引的整理日不代表所有功能的最低支援版號。遇到版本、腳本類型、資料權限或缺少簽章時，繼續查正式頁與目標環境，不從更新清單的名稱自行補出用法。

## 內容與授權界線

這個 ZIP 的 18 個檔案中未見 LICENSE、COPYING 或 NOTICE；本專案不據此推定可以將整包改以 MIT 散布。公開套件只新增自行撰寫的說明、識別索引與來源雜湊，未收錄上游手冊全文、策略範例、圖示或檢查器程式。權利聲明見 [第三方聲明](../THIRD_PARTY_NOTICES.md)。

本次新增 API 說明沒有在 XQ 編譯或執行。既有四類腳本的編譯證據仍只支持當時的測試案例，不能延伸為 SDT、Group、排行或全部新語法均已驗證。
