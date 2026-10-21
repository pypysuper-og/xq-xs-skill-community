![XQ × XS Community：台灣交易想法與 AI 腳本知識的連結](assets/readme-hero.png)

<div align="center">

# XQ × XS Community

### 用繁體中文，把交易想法寫成 XS。

**選股條件、技術指標、策略雷達、交易腳本——從一句想法，到有來源可查的程式草稿。**

[![Release v0.1.0](https://img.shields.io/badge/release-v0.1.0-0f766e?style=flat-square)](https://github.com/pypysuper-og/xq-xs-skill-community/releases/tag/v0.1.0) [![繁體中文](https://img.shields.io/badge/語言-繁體中文-2563eb?style=flat-square)](README.md) [![Community](https://img.shields.io/badge/社群維護-非官方-ea580c?style=flat-square)](xq-xs/THIRD_PARTY_NOTICES.md) [![MIT](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)](LICENSE)

[下載最新 Skill](https://github.com/pypysuper-og/xq-xs-skill-community/releases/latest) · [直接看 Skill](xq-xs/SKILL.md) · [原創範例](xq-xs/references/examples.md) · [回報問題](https://github.com/pypysuper-og/xq-xs-skill-community/issues)

</div>

你知道想找什麼股票、什麼時候觸發警示，卻卡在 XS 語法、欄位名稱，或一段看不懂的編譯錯誤？

**XQ × XS Community** 是一套面向台灣投資與交易者的 AI Agent Skill。讓支援 `SKILL.md` 的 AI 助手，依照整理好的 XS 規則與官方來源，協助你把想法寫成程式、讀懂既有腳本，並找出資料引用與交易狀態中的盲點。

你專注在交易邏輯；AI 協助查語法、整理程式與說明依據，最後在你的 XQ 環境中編譯、檢查與驗證。

## 先試一句話

```text
使用 $xq-xs 幫我寫一支台股日線選股腳本：
5 日均線上穿 20 日均線，輸出兩條均線的數值。
用繁體中文說明判斷邏輯、引用的官方來源，以及還需要在 XQ 驗證什麼。
```

這套 Skill 指引 AI 一併交付腳本類型、必要假設、程式、關鍵來源與實際驗證範圍。你能沿著說明回查，繼續調整自己的條件。

## 一套 Skill，涵蓋五種 XS 工作

| 你想做的事 | 可以怎麼問 | 主要產出 |
|---|---|---|
| **台股選股** | 幫我把均線、成交量、月營收條件寫成選股腳本 | 篩選條件、輸出欄位與資料說明 |
| **技術指標** | 幫我畫出兩條均線，並解釋每個參數 | 指標程式與計算邏輯 |
| **策略雷達／警示** | 價格突破時提醒我，檢查同根 K 棒是否重複觸發 | 警示條件與觸發範圍 |
| **自動交易腳本** | 審查待成交、部分成交和退出條件有沒有打架 | 部位／委託邏輯與待確認風險 |
| **自訂函數與除錯** | 解釋這段 XS，修正錯誤並保留原本的交易想法 | 可讀的說明、最小修正或重用函數 |

適合正在學 XS、已有腳本想繼續改，或希望先讓 AI 協助整理策略條件的使用者。交易腳本撰寫與實盤啟用是不同工作，實際送單需要你另外決定與驗證。

## 為台灣交易者多顧幾個細節

- **欄位相同，情境可能不同。** 資料、報價與選股欄位分開查，避免同名欄位套錯腳本。
- **看懂「上一期」到底是哪一期。** 釐清月營收、財報發布時間，以及欄位位移和日線變數位移的差別。
- **張、股、口與百分比要對得上。** 寫計算前先看市場、商品與欄位單位。
- **有進場訊號，也要看成交狀態。** 區分 `Position`、`Filled`、未成交與部分成交，檢查退出是否被擋住。
- **說明用繁體中文，來源能回查。** 函數與限制連回 XSHelp，範例連到官方固定版本。

這些判斷整理在 [資料與時間](xq-xs/references/data-and-time.md)、[選股與警示](xq-xs/references/screening-and-alerts.md) 及 [交易語義](xq-xs/references/autotrade.md)。

## 你會拿到什麼

| 內容 | 規模與用途 |
|---|---|
| **主題參考** | 9 份，依問題載入語法、資料、函數、警示與交易說明 |
| **離線名稱與來源索引** | 1,455 筆，涵蓋函數、關鍵字、欄位及 22 篇語法運用文章 |
| **官方範例路徑索引** | 1,419 支，附固定版本網址與 blob SHA |
| **原創 XS 範例** | 6 個，含數值／布林函數，交易範例預設關閉交易指令 |
| **離線查找工具** | Python 3.10+，不需第三方 Python 套件 |

索引讓 AI 先縮小查找範圍，再按需要開啟原文。上游手冊與官方程式保留在原出處，本專案提供重新整理的說明、識別索引與原創範例。

## 開始使用

### 1. 取得套件

到 [Releases](https://github.com/pypysuper-og/xq-xs-skill-community/releases/latest) 下載 `xq-xs-community-v0.1.0.zip` 並解壓。需要核對檔案時，使用同頁的 `.sha256` 檔。

也可以下載或 clone 本專案；要安裝的是完整 `xq-xs/` 資料夾。

### 2. 放進 AI 助手的 skills 目錄

保留 `SKILL.md`、`references/`、`data/`、`scripts/`、範例與授權檔的相對結構。以下以個人 Codex skills 為例，從解壓後含有 `xq-xs/` 的目錄執行：

```powershell
$skillHome = if ($env:CODEX_HOME) {
    $env:CODEX_HOME
} else {
    Join-Path $HOME '.codex'
}
$destination = Join-Path $skillHome 'skills\xq-xs'
if (Test-Path -LiteralPath $destination) {
    throw '同名 Skill 已存在，請先檢視差異再更新。'
}
New-Item -ItemType Directory -Force -Path (Split-Path $destination -Parent) | Out-Null
Copy-Item -LiteralPath '.\xq-xs' -Destination $destination -Recurse
```

其他支援 `SKILL.md` 的 AI agent 可放進各自的 skills 目錄，依該工具的方式重新載入。使用指令與參考文件本身不需要 Python；執行離線查找工具時才需要。

### 3. 帶著你的條件或錯誤訊息提問

```text
使用 $xq-xs 檢查我的腳本：
請保留原本的選股邏輯，說明錯誤原因，給我最小修正，
並列出是否需要核對資料頻率、發布時間或欄位單位。
```

如果問題涉及實際結果，附上商品、頻率、日期、腳本類型與錯誤訊息，會更容易定位。

## 官方來源與最新參考日期

**兩個主要 upstream 最新查閱日期：2026-10-21（台灣時間，UTC+8）。**

| 官方來源 | 本專案最新查閱日 | 查閱時的版本／範圍 |
|---|---|---|
| [XSHelp 線上說明書](https://xshelp.xq.com.tw/XSHelp/) | **2026-10-21** | 首頁列企業版 **v7.20.03**／個人版 **v3.20.03**；核心語法與 API 另參照個別頁面 |
| [sysjust-xq/XScript_Preset](https://github.com/sysjust-xq/XScript_Preset) | **2026-10-21** | `main` 最新 commit 為 [`d15a415`](https://github.com/sysjust-xq/XScript_Preset/commit/d15a4157ccb2c439b3633dec200808924a7f83a7)，提交日期 **2026-09-17**；索引固定於此版本 |

「查閱日」是本專案重新查看來源的日期，與上游提交日期不同。離線手冊索引來自提供的快照，其中整合文件標示 **2026-02-18**；**並未將全部索引條目逐項更新到 2026-10-21**。新函數、頻率、商品與版本支援，仍需使用時核對現行官方文件。完整說明見 [來源地圖](xq-xs/references/source-map.md) 與 [整併紀錄](docs/consolidation.md)。

## 想先查一個欄位？

從本專案根目錄執行：

```text
python xq-xs/scripts/lookup.py GetField --limit 3
python xq-xs/scripts/lookup.py 收盤價 --kind selection
python xq-xs/scripts/lookup.py "Position Filled" --source preset --json
python xq-xs/scripts/lookup.py 對位 --kind article
```

它只查隨附資料，不登入帳戶或送單。命中表示有該索引；查不到時，可改查正式名稱或官方網站。

## 驗證範圍與使用邊界

本專案已檢查 Skill 格式、工具行為、索引一致性、本地連結與 ZIP 解壓後的可攜使用。實際結果與指令見 [驗證紀錄](docs/validation.md)。

**六個原創 XS 範例尚未在 XQ 編譯或執行。** 請在自己的 XQ 環境完成編譯、資料核對與適當測試，再決定後續用途。回測、模擬與實盤各有不同證據；本專案不提供獲利保證或個人化投資建議。

## 一起讓台灣的 XS 使用更容易

歡迎透過 [Issues](https://github.com/pypysuper-og/xq-xs-skill-community/issues) 提出錯誤與改進。若涉及 API 或欄位，附上官方網址、XQ 版本與最小重現片段；分享前請移除帳號、憑證與個人資料。

維護者可參考 [更新與打包方式](docs/maintenance.md)。範例、Skill 入口與文件都在本專案中，方便追查與修改。

本專案由社群維護，與嘉實資訊／XQ 無隸屬或背書關係。原創內容與工具採 [MIT License](LICENSE)；保留既有 MIT Skill 的署名。外部網站、官方程式與商標的權利範圍見 [第三方聲明](xq-xs/THIRD_PARTY_NOTICES.md)。
