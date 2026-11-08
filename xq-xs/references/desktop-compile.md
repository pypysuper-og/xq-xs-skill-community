# 搭配 XQ 桌面編譯 XS

`scripts/xq_compile.py` 是可直接從命令列使用的桌面編譯橋接工具。Agent 可以寫 XS、呼叫 CLI、讀結果、修正後再編譯。CLI 本身不修改策略，也沒有執行、回測或送單命令。

## 使用前提與支援範圍

- Windows 互動桌面、Python 3.10+；不需第三方 Python 套件。實測是 Python 3.13.5。
- 建議用 uv 與隨附環境設定固定 Python 3.13.5；uv 本次實測版本是 0.9.25。
- **必須另外安裝、開啟並登入 XQ 個人版**，且只有一個可存取的執行個體。工具不處理帳密，也不會自行啟動 XQ。
- XScript 編輯器須可在該桌面操作。可以尚未開啟編輯器；工具會從已登入的主程式開啟。
- 操作期間讓鍵盤滑鼠空閒；工具會切換到 XQ。預設要求啟動前空閒 10 秒，偵測到失去 XQ 焦點就停止後續輸入。關閉既有的 XQ 模態對話框。
- XQ 與 Python 需要相容的桌面權限。鎖定桌面、服務帳戶、無頭 CI、遠端連線斷線及不同權限層級未經驗證。
- 實測 **XQ 個人版 `3.20.04 261006`**。依賴其選單、控制項與本機儲存格式；其他版本、企業版與不同介面語言需另作驗證。

**這不是 standalone XS compiler。** CLI 可以不透過 Agent 直接執行，但編譯仍由 XQ 完成。只有這個 Skill、只有 VS Code 擴充套件，或只有 Python，都不足以編譯 XS。普通查語法、寫作和離線查找不需要開啟 XQ。

## 指令

以下在 skill 目錄執行。`uv sync --locked` 依 `pyproject.toml`、`.python-version` 與 `uv.lock` 建立／同步 `.venv`；不需手動啟用環境，亦不把 `.venv` 放進套件。首次缺少指定 Python 時，uv 可能下載直譯器。`--locked` 在設定與鎖檔不一致時停止，不能在一般使用中任意重建鎖檔。參見 [uv 官方鎖定與同步說明](https://docs.astral.sh/uv/concepts/projects/sync/)。

來源是 UTF-8 `.xs`；中文亦可使用。若第一行有 `{@type:...}`，必須與 `--type` 一致；提交時移除這行匯出註解，並明確選取 XQ 類型。

```powershell
uv sync --locked
uv run --locked python scripts/xq_compile.py doctor --json
uv run --locked python scripts/xq_compile.py compile assets/examples/ma-indicator.xs --type indicator --work-dir ./compile-evidence --json
uv run --locked python scripts/xq_compile.py compile assets/examples/ma-screen.xs --type filter --work-dir ./compile-evidence --json
uv run --locked python scripts/xq_compile.py compile assets/examples/ma-alert.xs --type sensor --work-dir ./compile-evidence --json
uv run --locked python scripts/xq_compile.py compile assets/examples/ma-autotrade-disabled.xs --type autotrade --work-dir ./compile-evidence --json
```

其他工作目錄可用 `uv run --locked --project <skill-folder> python <script-path> ...`；腳本與 XS 檔案路徑仍相對於目前工作目錄。保留直接 `python` 的使用方式，但它不套用 uv 的版本鎖定。維護者若需改版本，應明確更新設定及鎖檔並重新驗證，不只手動替換虛擬環境。

`doctor` 只讀取執行個體、登入狀態及版本，不操作編輯器；`ready` 不保證下一次 UI 操作一定成功。四個 `--type` 分別對應指標、選股、警示與交易。自訂函數、批次編譯、回測及策略部署目前不在此工具範圍。

每次編譯產生一個新的 `XSC...` 名稱及 XQ 腳本，保留原有腳本；修正後再次呼叫也會建立新名稱。工具會核對新腳本類型與編輯器中的完整來源，再送一次 F6。它不自動刪除測試腳本。使用者可事後在 XQ 檢視、整理這些腳本。

`--work-dir` 必填，會保存來源快照、請求及結果。`--timeout` 預設 120 秒，可設 10–300；`--idle-seconds` 預設 10，可設 0–60。可用 `--xq-exe` 限定執行檔；若無法自動辨識本機腳本資料庫，可用 `--script-store` 指定。這兩項不會啟動程式或寫入資料庫。

## 如何判讀結果

| 結束碼／status | 含義與下一步 |
|---|---|
| `0` / `ready`、`passed` | doctor 前提成立，或該次編譯輸出成功；區分所執行的命令 |
| `1` / `compile_error` | XQ 明確回報編譯失敗；依錯誤與來源作最小修正 |
| `2` / `environment_error` | 版本、權限、控制項、來源驗證或資料格式不符；先處理環境 |
| `3` / `timeout` | 未在期限內取得結果；可能已送出 F6，先查看 XQ，避免盲目重送 |
| `4` / `desktop_busy` | 桌面正在使用、已有對話框，或另一個 CLI 正在編譯；待空閒後再試 |

成功／失敗以包含**本次唯一腳本名稱**的 XQ 編譯輸出確認；不以舊結果、檔案存在或視窗出現當作成功。JSON 包含來源雜湊、類型、XQ 版本、`source_matches`、`type_matches`、輸出與 `evidence_dir`。

詳細錯誤有兩種讀取方式：

1. XQ 若有保存文字，工具以唯讀方式查詢該唯一名稱的本機紀錄，回傳 `diagnostics` 與 `raw_compiler_messages`。不解碼或寫入資料庫中的其他腳本。
2. 有些前端語法錯誤只出現在結果表格，本機紀錄仍是未編譯狀態。此時照樣回傳 `compile_error`、錯誤數及 `diagnostic_detail_available: false`，並嘗試保存可見表格為 `diagnostic_image`。Agent 使用可讀取本地圖片的工具查看圖片，再與來源核對。

**行號與欄位沒有結構化擷取，JSON 中為 `null`。** 表格圖片只是當時可見的列，未保證包含全部錯誤或未被截斷的描述。若圖片捕捉失敗，結果另列 `diagnostic_capture_error`；沒有錯誤細節時應請使用者提供 XQ 訊息，不能猜測診斷。原始編譯輸出中的錯誤數、去重後文字數與表格列數可能不同，不應互相替代。

圖片中的位置對應 `submitted_source` 快照。由於匯入時移除開頭類型註解，與原始檔可能相差一行或更多；`source_line_offset` 記錄移除的前置行數。修正時先比對提交快照，再定位原始檔，不直接把表格行號套回原始檔。

工具不使用 OCR 或剪貼簿讀取診斷；只有 Agent 看圖時才涉及圖像辨識。截圖讀到的位置或文字應明示來自圖片，不能冒稱編譯器已提供結構化欄位。

## Agent 的修正流程

先確認使用者已授權操作這台 XQ 桌面，再執行 doctor 與一次 compile。讀 `status`，失敗時先用文字診斷；缺文字再看 `diagnostic_image`。將錯誤與同一份來源快照比對，保留原交易邏輯，修改後重新編譯。

預設最多兩次修正；使用者指定更小範圍時遵守較小範圍。連續相同問題沒有新證據、結果不明、桌面被接手或需要改變策略含義時停止，交付已知錯誤與缺口。不要把環境錯誤當成語法問題，也不要因逾時而直接連續重送 F6。

桌面工具若提供使用者控制權檢查，必須透過該工具執行 CLI；`--idle-seconds` 是本機輔助檢查，不能覆蓋平台的控制權限制。

## 驗證與資料保留

2026-11-09 於上述 XQ 版本實測四種類型，各完成正確例通過、未宣告識別字失敗、依診斷修正後通過。選股負例使用了編譯輸出與表格圖片備援；其他三類取得本機診斷文字。這支持這些案例的桌面編譯流程，沒有驗證所有 XS 語法或不同 XQ 版本。

原始證據包含程式內容、本機路徑、腳本識別及可能的私人資訊；保留在使用者指定的本機目錄，分享前先檢視。工具不會自動上傳證據。

這些測試**沒有執行腳本、回測、啟用策略、連接券商或送單**。交易範例的 `EnableOrders` 預設為 `false`。編譯通過只代表該版本接受程式，不能推論策略或實盤已驗證。
