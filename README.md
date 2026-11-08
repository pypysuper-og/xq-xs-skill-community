![XQ × XS Community：台灣交易想法與 AI 腳本知識的連結](assets/readme-hero.png)

<div align="center">

# XQ × XS Community

### 用繁體中文，把交易想法寫成 XS。

**選股條件、技術指標、策略雷達、交易腳本——從一句想法，到有來源可查的程式草稿。**

[![Release v0.3.0](https://img.shields.io/badge/release-v0.3.0-0f766e?style=flat-square)](https://github.com/pypysuper-og/xq-xs-skill-community/releases/tag/v0.3.0) [![繁體中文](https://img.shields.io/badge/語言-繁體中文-2563eb?style=flat-square)](README.md) [![Community](https://img.shields.io/badge/社群維護-非官方-ea580c?style=flat-square)](xq-xs/THIRD_PARTY_NOTICES.md) [![MIT](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)](LICENSE)

[下載最新 Skill](https://github.com/pypysuper-og/xq-xs-skill-community/releases/latest) · [直接看 Skill](xq-xs/SKILL.md) · [原創範例](xq-xs/references/examples.md) · [回報問題](https://github.com/pypysuper-og/xq-xs-skill-community/issues)

</div>

你知道想找什麼股票、什麼時候觸發警示，卻卡在 XS 語法、欄位名稱，或一段看不懂的編譯錯誤？

**XQ × XS Community** 是一套面向台灣投資與交易者的 AI Agent Skill。讓支援 `SKILL.md` 的 AI 助手，依照整理好的 XS 規則與官方來源，協助你把想法寫成程式、讀懂既有腳本，並找出資料引用與交易狀態中的盲點。

你專注在交易邏輯；AI 協助查語法、整理程式與說明依據，最後在你的 XQ 環境中編譯、檢查與驗證。

## v0.3.0：補進官方 Skill 的實用參考

已下載並檢查 [XQ〈用 ChatGPT 寫 XS 腳本〉](https://www.xq.com.tw/xstrader/%E7%94%A8chatgpt%E5%AF%ABxs%E8%85%B3%E6%9C%AC/) 所附的 xscript ZIP，從中挑出 SDT、Group、版本與資料語義等值得整合的部分，再核對代表性的官方頁面。

- 新增 [SDT／Group 參考](xq-xs/references/data-structures.md)，說明商品表、策略共享表、條件寫入與商品清單的用途。
- 加入 50 筆補充識別資料：38 個 SDT 名稱與 12 項 API／宣告；CLI 以 `--source supplement` 或 `all` 查找，JSON 保留查證日與證據層級。
- 補充資料對位、欄位支援／缺值、統計與輸出參數，以及跨頻率文件的版本差異。

本次發布的是重新撰寫的摘要與來源資訊。來源包未附授權檔，沒有將其手冊、範例或 checker 直接納入；完整採用範圍與 ZIP 雜湊見 [上游審查](xq-xs/references/upstream-xscript.md)。新增 API 參考尚未做 XQ 實機編譯或執行。

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
| **主題參考** | 14 份，含語法、資料、SDT／Group、函數、警示、交易、桌面編譯、編輯器規則、文章案例與上游審查 |
| **離線名稱與來源索引** | 1,455 筆，涵蓋函數、關鍵字、欄位及 22 篇語法運用文章 |
| **官方範例路徑索引** | 1,419 支，附固定版本網址與 blob SHA |
| **原創 XS 範例** | 6 個，含數值／布林函數，交易範例預設關閉交易指令 |
| **離線查找工具** | Python 3.10+，不需第三方 Python 套件 |
| **程式語法文章索引** | 12 篇：分類頁 11 篇，加指定的 ChatGPT／XS 文章，保留刊登日期與官方連結 |
| **補充 API 索引** | 50 筆官方識別 metadata，區分清單可見與已閱讀個別頁面 |
| **官方編輯器規則** | 固定版本的 XS TextMate grammar 與語言設定，附 MIT 署名 |
| **桌面編譯 CLI** | 搭配 XQ 個人版，匯入、核對來源與類型、編譯並讀回結果 |

索引讓 AI 先縮小查找範圍，再按需要開啟原文。上游手冊與官方程式保留在原出處，本專案提供重新整理的說明、識別索引與原創範例。

## 讓 Agent 寫 XS，再交給 XQ 編譯

自 v0.2.0 起附桌面編譯工具，讓 Agent 執行「寫程式 → CLI 編譯 → 讀錯誤 → 修正 → 再編譯」。**必須另外安裝、開啟並登入 XQ 個人版，並提供可互動的 Windows 桌面。** Skill 本身沒有附獨立 XS 編譯器；CLI 可以直接使用，但編譯工作仍由 XQ 完成。只查語法與寫作不需要開啟 XQ。

建議使用 [uv](https://docs.astral.sh/uv/) 管理 Python 環境。套件內附 `pyproject.toml`、`.python-version` 與 `uv.lock`，固定已實測的 **Python 3.13.5**，目前零第三方 Python 依賴。uv 會在 Skill 目錄建立自己的 `.venv`，不需手動啟用；v0.2.0 及後續 Release ZIP 均包含這些設定。

以下從本專案根目錄執行。操作期間讓鍵盤滑鼠空閒，工具會切換到 XQ：

```powershell
uv sync --locked --project xq-xs
uv run --locked --project xq-xs python xq-xs/scripts/xq_compile.py doctor --json
uv run --locked --project xq-xs python xq-xs/scripts/xq_compile.py compile xq-xs/assets/examples/ma-indicator.xs --type indicator --work-dir ./compile-evidence --json
```

`--locked` 會在環境設定與鎖檔不一致時報錯，避免一般執行時改寫鎖檔；`uv sync --locked` 依鎖檔同步環境。首次若沒有指定 Python，uv 可能需要下載。保留三個設定檔，讓每台電腦自行建立環境，不要搬移 `.venv`。Python 環境與 XQ 版本是兩件事，uv 不會固定 XQ 的桌面介面。工具仍可直接用 Python 3.10+ 執行，但該方式不套用本專案的版本鎖定。

CLI 每次建立獨立測試腳本，先比對編輯器來源與類型，再觸發一次 F6。回傳成功／失敗、錯誤數與本機證據位置；有文字診斷就回傳文字，只有桌面表格有錯誤時保存可見表格圖片，供 Agent 讀圖修正。**行號與欄位目前沒有結構化擷取，也未保證取得所有錯誤的完整文字。**

已在 XQ 個人版 **`3.20.04 261006`** 實測以下流程：

| 腳本類型 | 正確腳本 | 故意未宣告識別字 | 依診斷修正後 |
|---|---|---|---|
| 指標 `indicator` | 通過 | 確認失敗 | 通過 |
| 選股 `filter` | 通過 | 確認失敗；詳細訊息以表格圖片讀取 | 通過 |
| 警示 `sensor` | 通過 | 確認失敗 | 通過 |
| 交易 `autotrade` | 通過 | 確認失敗 | 通過 |

實測只編譯，沒有執行策略、回測或送單。此工具依賴 XQ 桌面介面，尚未驗證無頭 CI、鎖定桌面或其他 XQ 版本；自訂函數目前不在 CLI 支援範圍。完整前提、結束碼與 Agent 修正流程見 [桌面編譯指南](xq-xs/references/desktop-compile.md)，實測證據範圍見 [編譯驗證紀錄](docs/compilation-validation.md)。

**v0.3.0 Release ZIP 保留桌面編譯工具及 uv 環境設定；既有 v0.1.0 ZIP 不含這些功能。** 安裝或更新時保留完整 `xq-xs/` 資料夾。

## 開始使用

### 1. 取得套件

到 [Releases](https://github.com/pypysuper-og/xq-xs-skill-community/releases/latest) 下載 `xq-xs-community-v0.3.0.zip` 並解壓。需要核對檔案時，使用同頁的 `.sha256` 檔。

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

其他支援 `SKILL.md` 的 AI agent 可放進各自的 skills 目錄，依該工具的方式重新載入。閱讀參考文件本身不需要 Python；執行離線查找或桌面編譯工具時才需要。桌面編譯另外需要上述 XQ 環境。

### 3. 帶著你的條件或錯誤訊息提問

```text
使用 $xq-xs 檢查我的腳本：
請保留原本的選股邏輯，說明錯誤原因，給我最小修正，
並列出是否需要核對資料頻率、發布時間或欄位單位。
```

如果問題涉及實際結果，附上商品、頻率、日期、腳本類型與錯誤訊息，會更容易定位。

## 官方來源與最新參考日期

**主要索引查閱基準為 2026-10-21；官方 Skill 與精選 API 補充於 2026-11-09 核對。**

| 官方來源 | 本專案最新查閱日 | 查閱時的版本／範圍 |
|---|---|---|
| [XSHelp 線上說明書](https://xshelp.xq.com.tw/XSHelp/) | **2026-10-21** | 首頁列企業版 **v7.20.03**／個人版 **v3.20.03**；核心語法與 API 另參照個別頁面 |
| [sysjust-xq/XScript_Preset](https://github.com/sysjust-xq/XScript_Preset) | **2026-10-21** | `main` 最新 commit 為 [`d15a415`](https://github.com/sysjust-xq/XScript_Preset/commit/d15a4157ccb2c439b3633dec200808924a7f83a7)，提交日期 **2026-09-17**；索引固定於此版本 |
| [官方 XS VS Code 擴充套件](https://marketplace.visualstudio.com/items?itemName=sysjust-xq.xs) | **2026-11-09** | 1.0.2／固定於 2023-04-26 的 [`c6101a5`](https://github.com/sysjust-xq/vscode-xs/commit/c6101a57676990160de656171bd72638d5758102)；只作編輯器規則參考 |
| [XQ 程式語法文章](https://www.xq.com.tw/xstrader/category/程式語法/) | **2026-11-09** | 指定分類頁可見的 11 篇文章，附案例導讀；不是完整網站或即時 API 規格 |
| [〈用 ChatGPT 寫 XS 腳本〉與所附 Skill](https://www.xq.com.tw/xstrader/%E7%94%A8chatgpt%E5%AF%ABxs%E8%85%B3%E6%9C%AC/) | **2026-11-09** | 文章刊於 2026-10-01，取得的 ZIP 修改於 2026-10-15；採用範圍及雜湊另有記錄 |
| [SDT 官方清單](https://xshelp.xq.com.tw/XSHelp/lists?a=SDTFUNC) 與補充 API | **2026-11-09** | 38 個 SDT 名稱，加 12 項個別函數／宣告；證據層級隨索引保留 |

「查閱日」是本專案重新查看來源的日期，與上游提交日期不同。離線手冊索引來自提供的快照，其中整合文件標示 **2026-02-18**；**並未將全部索引條目逐項更新到 2026-10-21**。新函數、頻率、商品與版本支援，仍需使用時核對現行官方文件。完整說明見 [來源地圖](xq-xs/references/source-map.md) 與 [整併紀錄](docs/consolidation.md)。

## 想先查一個欄位？

從本專案根目錄執行：

```text
python xq-xs/scripts/lookup.py GetField --limit 3
python xq-xs/scripts/lookup.py 收盤價 --kind selection
python xq-xs/scripts/lookup.py "Position Filled" --source preset --json
python xq-xs/scripts/lookup.py 對位 --kind article
python xq-xs/scripts/lookup.py 跨頻率 --source articles --json
uv run --locked --project xq-xs python xq-xs/scripts/lookup.py SDT_GetValue --source supplement --json
```

它只查隨附資料，不登入帳戶或送單。預設仍查 `help`，使用 `--source all` 可合併四個索引；相同名稱可能有不同來源與日期。補充索引的 `catalog-entry` 表示清單可見，`help-page` 表示讀過個別說明頁，均不代表編譯通過。查不到時，可改查正式名稱或官方網站。

## 驗證範圍與使用邊界

本專案已檢查 Skill 格式、工具行為、索引一致性、本地連結與 ZIP 解壓後的可攜使用。實際結果與指令見 [驗證紀錄](docs/validation.md)。

**四個均線範例已在上述 XQ 版本編譯通過，兩個自訂函數尚未實機編譯；全部均未執行或回測。** 請在自己的 XQ 環境核對資料與進行適當測試，再決定後續用途。回測、模擬與實盤各有不同證據；本專案不提供獲利保證或個人化投資建議。

## 一起讓台灣的 XS 使用更容易

歡迎透過 [Issues](https://github.com/pypysuper-og/xq-xs-skill-community/issues) 提出錯誤與改進。若涉及 API 或欄位，附上官方網址、XQ 版本與最小重現片段；分享前請移除帳號、憑證與個人資料。

維護者可參考 [更新與打包方式](docs/maintenance.md)。範例、Skill 入口與文件都在本專案中，方便追查與修改。

本專案由社群維護，與嘉實資訊／XQ 無隸屬或背書關係。原創內容與工具採 [MIT License](LICENSE)；保留既有 MIT Skill 的署名。外部網站、官方程式與商標的權利範圍見 [第三方聲明](xq-xs/THIRD_PARTY_NOTICES.md)。
