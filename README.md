# XQ／XS AI Agent Skill

協助 AI agent 撰寫、解釋、除錯與審查 XQ 平台的 XS／XScript。支援指標、警示／策略雷達、選股、自動交易與自訂函數，以繁體中文說明，並按任務查證官方語義。

這是非官方 skill，並非 XS compiler。隨附範例尚未在 XQ 編譯或執行；程式的實際驗證範圍必須另行說明。

## 包含什麼

- **單一 skill 入口**：`xq-xs`，以九份主題參考分流，不將整本手冊塞入上下文。
- **1,455 筆離線查找項目**：函數、關鍵字、報價、資料、選股欄位與 22 篇語法運用文章；同名欄位依命名空間保留。
- **1,419 支官方範例的路徑索引**：固定到可追查的 upstream commit，附 blob SHA 與網址；不包含上游程式本體。
- **六個原創 XS 範例**：五類腳本，另區分數值／布林函數。交易範例預設關閉交易指令。
- **無第三方 Python 相依的工具**：離線查找、重建索引、套件檢查與 ZIP 打包，使用 Python 3.10+。

## 安裝

將整個 [xq-xs/](xq-xs/) 放進目標 agent 支援的 skills 目錄，保留其相對結構與授權檔。不要只複製 `SKILL.md`。

例如從本專案根目錄複製到個人 Codex skills：

```powershell
$skillHome = if ($env:CODEX_HOME) {
    $env:CODEX_HOME
} else {
    Join-Path $HOME '.codex'
}
$destination = Join-Path $skillHome 'skills\xq-xs'
if (Test-Path -LiteralPath $destination) {
    throw '目的 skill 已存在，請先檢視差異並自行選擇更新方式。'
}
New-Item -ItemType Directory -Force -Path (Split-Path $destination -Parent) | Out-Null
Copy-Item -LiteralPath '.\xq-xs' -Destination $destination -Recurse
```

依 agent 的方式重新載入 skill 後，以 `$xq-xs` 明確叫用；其他支援 `SKILL.md` 的 agent 也可使用。工具不要求 GitHub connector、特定模型或外部服務，查現行官方原文時才需要網路能力。

## 使用範例

```text
使用 $xq-xs 寫一支台股日線選股腳本：5 日均線上穿 20 日均線，
輸出兩條均線，並說明尚未在 XQ 驗證的項目。
```

```text
使用 $xq-xs 審查這支交易腳本，特別檢查未成交、部分成交、
同次洗價的交易指令優先順序，以及 Position 與 Filled 的更新。
```

```text
使用 $xq-xs 檢查我用日線變數 [1] 取得上月營收的寫法，
說明 GetField 的期別、對位和資料發布時間差異。
```

不需要 Python 也能閱讀 skill 與參考文件。需要快速找到來源時，從專案根目錄執行：

```text
python xq-xs/scripts/lookup.py GetField --limit 3
python xq-xs/scripts/lookup.py 收盤價 --kind selection
python xq-xs/scripts/lookup.py "Position Filled" --source preset --json
python xq-xs/scripts/lookup.py 對位 --kind article
```

命中只表示索引裡有該名稱；查無結果不表示 XS 不支援。索引不是目前全部 API 清單，來源日期與查證方法見 [來源地圖](xq-xs/references/source-map.md)。

## 文件與結構

| 位置 | 用途 |
|---|---|
| [xq-xs/SKILL.md](xq-xs/SKILL.md) | Agent 的唯一 skill 入口與參考分流 |
| [xq-xs/references/](xq-xs/references/) | 語法、類型、資料／時間、函數／狀態、選股／警示、交易、審查、來源及範例 |
| [xq-xs/assets/examples/](xq-xs/assets/examples/) | 可分別匯入對應腳本類型的原創範例 |
| [xq-xs/data/](xq-xs/data/) | 去重後的識別名稱與固定版本檔案索引 |
| [docs/consolidation.md](docs/consolidation.md) | 整併來源、覆蓋範圍與矛盾校正 |
| [docs/maintenance.md](docs/maintenance.md) | 更新來源、重建、驗證與打包 |
| [docs/validation.md](docs/validation.md) | 本版本實際驗證結果與尚未驗證項目 |
| [tests/](tests/) | 索引、查找與可攜套件的行為測試 |

發送或安裝的最小單位是 `xq-xs/`；根目錄的維護工具、測試與整併文件不需一起載入 agent。

## 驗證與打包

```text
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/build_package.py
```

打包結果為 `dist/xq-xs.zip` 及其 SHA-256 檔；`dist/` 是忽略的建置輸出。ZIP 保留完整 skill、工具、索引、原創範例與授權聲明，不包含原始抓取全文或維護用來源。

以上檢查驗證 skill 套件與 Python 工具，**不會編譯 XS**。XQ 編譯、指定資料回測、模擬交易及實盤觀察，是需要各自證據的不同項目。本套件也不登入帳戶、啟動策略或發送委託。

## 來源與授權

核心官方來源為 [XSHelp](https://xshelp.xq.com.tw/XSHelp/) 與 [sysjust-xq/XScript_Preset](https://github.com/sysjust-xq/XScript_Preset)。本套件將既有 skill 與提供的手冊材料整理為原創摘要及識別索引，不鏡像外部手冊與程式。

本套件原創內容與工具採 [MIT License](LICENSE)，保留既有 MIT skill 的署名；外部內容與商標權利不由此授權。詳見 [第三方聲明](xq-xs/THIRD_PARTY_NOTICES.md)。
