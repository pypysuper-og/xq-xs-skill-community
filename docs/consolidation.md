# 整併來源與覆蓋範圍

## 整理方式

本版本將兩份 XS skill 草稿、八份參考文件及官方線上來源整理成一個 `xq-xs` skill。入口只保留會影響 agent 決策的規則；細節分到主題參考，龐大原文則轉為名稱與來源索引。使用者資料夾與未授權的上游全文不包含在套件中。

| 輸入 | 採用方式 |
|---|---|
| 既有 `xq-xs-skill` | 沿用名稱與 MIT 署名，重寫入口、補強分流與來源證據 |
| 另一份 `xs_script_skill` 草稿 | 提取五類腳本的需求範圍，校正 frontmatter、函數型別與交易語義；不收錄全文 |
| `關鍵字.md` | 關鍵字與宣告名稱、分類、原始 URL |
| `內建.md`／`系統.md` | 函數名稱、分類與 URL，不複製函數說明或程式 |
| `報價.md`／`資料.md`／`選股.md` | 分開命名空間，保留同名欄位的不同情境 |
| `XS語法運用.md` | 22 篇有標題的文章連結；一列空白導覽資料明確排除 |
| `all_documentation.md` | 1,406 個條目與分類，補足分檔未收錄名稱，與其他來源合併去重 |
| [XSHelp](https://xshelp.xq.com.tw/XSHelp/) | 查證當前核心 API 與限制，原創摘要附確切連結 |
| [XScript_Preset](https://github.com/sysjust-xq/XScript_Preset) | 完整遞迴樹的 `.xs` 路徑、blob SHA、固定 commit 連結，另讀代表性腳本核對語義 |

## 數量與去重規則

八份文件共取得 **2,822 筆有效條目紀錄**，按「命名空間＋不區分大小寫的名稱」合併成 **1,455 筆**。多個分類、來源文件與替代網址保留，不丟失同名欄位在不同腳本情境的差異。

| 類型 | 去重後筆數 |
|---|---:|
| 內建函數 `builtin` | 179 |
| 系統函數 `system` | 216 |
| 關鍵字 `keyword` | 33 |
| 報價欄位 `quote` | 126 |
| 資料欄位 `data` | 362 |
| 選股欄位 `selection` | 517 |
| 語法運用文章 `article` | 22 |

其中 **83 筆**只有名稱與分類，缺少原始直達網址；索引明確使用 `link_type: search`，連到官方搜尋，不推測 help group。每份輸入的 SHA-256、有效筆數與排除筆數記於 [help-index.json](../xq-xs/data/help-index.json)。

官方 preset 的 **1,419 個 `.xs` 檔案**分為函數 275、指標 397、交易 64、警示 359、選股 324。其他檔案例如上游 README 不算腳本。版本固定為 [`d15a4157ccb2c439b3633dec200808924a7f83a7`](https://github.com/sysjust-xq/XScript_Preset/commit/d15a4157ccb2c439b3633dec200808924a7f83a7)，其 commit 日期為 2026-09-17；檔案樹在整併時由官方 GitHub API 讀取且未截斷。

對應的 tree object 為 `59c1504ac66a81969122ca9df2e7e2c24c94c7e7`，以實際 tree SHA 重新取得後確認所有檔案路徑／blob 身分相同。索引分別保存 commit 與 tree 身分，不將別名回應混記為 tree object。

## 已校正的矛盾

- **Skill 格式與名稱**：使用有效 YAML frontmatter 和單一 `xq-xs` 名稱，不保留兩個相互競爭的入口。
- **函數回傳型別**：一份草稿將 `function_bool` 視為未證實，另一份使用 `function_num`。實讀官方 `Average.xs` 與 `CrossOver.xs` 後，確認數值 `function` 與布林 `function_bool` 均有實例；未經證實的別名不繼續傳播。
- **型別標頭的證據**：將 `{@type:...}` 說明為官方匯出註解慣例，並要求編輯器類型一致；不將註解本身當成 runtime 或編譯通過的證據。
- **選股輸出**：確認 `OutputField` 與編號形式都是正式語法；新範例採容易閱讀的帶序號／名稱形式。
- **交易時序**：補上同次洗價的固定部位快照、第一個交易指令生效，以及策略相對部位不等於帳戶庫存。
- **時間序列**：補上資料欄位頻率位移與主頻率變數位移的差異；不以最新報價冒充歷史資料。
- **驗證用語**：套件檢查、XS 編譯、回測、模擬與實盤分別記錄，不由其中一項推導其他結果。

校正依據與逐項連結在 [腳本類型](../xq-xs/references/script-types.md)、[資料與時間](../xq-xs/references/data-and-time.md)、[交易](../xq-xs/references/autotrade.md) 與 [來源地圖](../xq-xs/references/source-map.md)。

## 來源身分與時效

既有 MIT skill 的參考 commit 為 `deb3499b382a61238a6194a9a80bfb75d10edc34`。兩份 skill 入口的原始 SHA-256 分別為：

```text
xq-xs/SKILL.md
73e69f70fb379816bfdc4fdd0b70be6262ac5b515a9c313198505bf862d19909

xs_script_skill/SKILL.md
9f35dfcfe06c889ee93c57f001b19410a93a21e830ab6978bb816d0b1f09c741
```

整併日期為 **2026-10-21**。`all_documentation.md` 自述產生日期為 2026-02-18；其他離線材料不當作當前完整規格。這次僅對核心決策所需頁面與代表性官方程式進行線上查證，沒有逐項打開所有索引連結，也沒有在 XQ 編譯或執行。

官方首頁在查證時顯示企業版 v7.20.03／個人版 v3.20.03 的更新說明；這是網頁觀察，並未驗證特定使用者安裝版本。新 API、版本與商品支援仍需使用時即時核對。

授權與不收錄上游原文的理由見 [第三方聲明](../xq-xs/THIRD_PARTY_NOTICES.md)。
