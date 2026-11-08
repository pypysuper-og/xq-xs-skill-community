# 驗證紀錄

## v0.3.0：官方 Skill 參考與補充索引（2026-11-09）

使用 uv 0.9.25、Python 3.13.5，**42 項測試全部通過**。新增測試涵蓋 SDT 的獨立／合併來源查找、證據日期與層級、錯誤類別拒絕、ChatGPT 文章查找，以及拒絕把內文、其他官方名稱、外站 URL 或「已編譯」宣稱混進補充索引。套件測試另驗證新 JSON、兩份參考文件與解壓後查找。

以下是可重現入口；本次以 unittest discover API 指定單次測試暫存位置，執行同一套測試：

```text
uv run --locked --project xq-xs python -m unittest discover -s tests -v
uv run --locked --project xq-xs python scripts/validate_repository.py
uv run --locked --project xq-xs python scripts/build_package.py --output dist/xq-xs-community-v0.3.0.zip
```

validator 檢查 55 份 UTF-8 來源、本地連結、私人路徑、既有 1,455／1,419 筆索引與新補充索引；新增檢查核對名稱與官方 URL 的命名空間、逐項證據層級及上游成員大小／雜湊格式。這些均為離線結構檢查，不重新連線證實每個 API。skill-creator frontmatter 檢查通過。

來源查證包括文章實際下載連結、取得的 ZIP 與 18 個成員雜湊，以及 SDT 清單的 38 個名稱／URL。另讀取補充索引中的 12 項函數／宣告頁與 4 個代表性 SDT 頁，並對照官方教學及固定 commit 的 `xfMin_EMA` 原始碼。大型上游範例只作結構與導航檢視；未執行上游 checker，也未全面刷新既有手冊索引。詳見 [採用範圍](../xq-xs/references/upstream-xscript.md)。

正式 ZIP 為 **38 個檔案、183,073 bytes**，SHA-256：

```text
5f040b10d602d557e63f0950fc7a0db64302b71528f2e11d73fe4e0ead86713d
```

已核對 CRC 及每個封裝檔案與來源相同，並在獨立解壓位置用 `uv run --locked --offline --project ...` 建立該位置的 Python 3.13.5 環境，實測 SDT／Group／新文章查找、編譯 CLI `--help` 及 Windows adapter 匯入。三個環境設定檔未被改寫。公開來源與 ZIP 的私人路徑、常見 token／private-key／含憑證 URL 掃描未命中；此掃描不代表完整的秘密資訊偵測保證。

本版桌面編譯的兩個 Python 檔案與前版完全相同，沒有操作 XQ。四類編譯案例仍沿用下方既有證據；本版新增的 SDT、Group、排行或欄位語義說明**尚未進行實機編譯或執行**，不據此聲稱回測或交易行為已驗證。

## v0.2.0：桌面編譯與擴充參考（2026-11-09）

Windows、Python **3.13.5**。38 項測試已通過，涵蓋既有索引與可攜套件，以及新文章查找、UTF-8／類型註解正規化、唯讀精確名稱查詢、epoch 含毫秒的未編譯狀態、唯一腳本名稱的終止輸出、來源矛盾拒絕、缺少文字診斷，以及觸發後異常仍保留證據。實際使用 `unittest` discover API 執行，將測試暫存目錄指定到操作者的工作目錄。可重現入口：

```text
uv run --locked --project xq-xs python -m unittest discover -s tests -v
uv run --locked --project xq-xs python scripts/validate_repository.py
```

套件測試會解壓 ZIP，從其他目錄執行查找與編譯 CLI `--help`，並核對文章與編輯器來源。validator 已擴充核對文章日期與官方 URL、兩份 MIT 編輯器資產的固定 blob SHA（允許單一檔尾換行），並排除本機 `.venv`。skill-creator 的 `quick_validate.py` 結果為 `Skill is valid!`；該工具不屬於套件執行依賴。

實機已在 **XQ 個人版 3.20.04 261006** 完成四類正確例、故意錯誤例與修正後重編譯。詳細時間、結果與限制見 [編譯驗證紀錄](compilation-validation.md)。四個均線範例通過編譯，兩個自訂函數尚未實機編譯；全部未執行或回測。套件測試使用假資料，不冒充 XQ 實機證據。

新增 uv 設定固定 Python 3.13.5、零第三方依賴；本機 uv 是 0.9.25。套件包含設定及鎖檔，不包含 `.venv`。一般執行採 `--locked`，不自動變更鎖檔。uv 只管理 Python 環境，不能替代 XQ 安裝與桌面條件。

加入 uv 打包設定後，於該 uv 環境執行受影響的 3 項套件測試，全部通過。另將預覽 ZIP 解壓到不同目錄，核對 CRC 及 34 個封裝檔案與來源相同，實際以 `uv run --locked --offline --project ...` 建立當地 `.venv`，確認 Python 3.13.5、文章查找、CLI `--help` 及 Windows adapter 匯入。刻意改動解壓副本的專案版本後，`--locked` 正確拒絕執行，鎖檔保持不變；恢復副本設定後結束測試。這次 uv 可攜性測試沒有操作 XQ 桌面，實機編譯沿用上面的同版本 Python 證據。

同日讀取官方 VS Code 擴充套件原始碼與 MIT 授權，固定到 `c6101a57676990160de656171bd72638d5758102`，另整理指定分類頁的 11 篇歷史文章。既有手冊與 preset 的查閱日期仍為 2026-10-21，沒有把全部舊索引逐項重新查證。

v0.2.0 發布套件包含桌面編譯工具、參考文件及 uv 設定；既有 v0.1.0 ZIP 不含桌面編譯工具。正式套件建置入口：

```text
uv run --locked --project xq-xs python scripts/build_package.py --output dist/xq-xs-community-v0.2.0.zip
```

尚未驗證其他 XQ 版本／企業版、無頭或鎖定桌面、斷線／不同權限層級、所有錯誤列的完整擷取、Python 3.10 實機執行或 Agent 自動選用與安裝啟用。編譯通過不支持回測、獲利或實盤就緒宣稱。

發布版號與鎖檔改為 0.2.0，不改變 Python 版本、依賴或桌面編譯程式。沿用已記錄的 XQ 實測，並核對正式 ZIP 與 tag 來源的檔案內容；下載資產與 SHA-256 可由 [v0.2.0 Release](https://github.com/pypysuper-og/xq-xs-skill-community/releases/tag/v0.2.0) 查驗。

## v0.1.0 的歷史驗證

以下內容僅記錄 **2026-10-21 當時** 的套件檢查；當時尚未進行的四類編譯，已由上方 2026-11-09 紀錄補充。執行環境：Windows、Python **3.13.5**。

## 已執行

```text
python -m unittest discover -s tests -v
```

**21 項測試通過。** 包含多行來源解析、關鍵字不同 URL 格式、重複名稱與命名空間、無直達網址的搜尋連結、截斷檔案樹與異常路徑拒絕、含 `#` 的 preset 路徑編碼、中文 JSON、查找結果排序及結束碼。

最終來源身分核對另加入一項 regression：commit 別名不得被當成 tree object。先確認新測試在修正前失敗，再補上拒絕條件，針對樹身分／完整性與套件抽離情境執行下列檢查，**7 項通過**。測試庫現有 22 項；未受影響的檢查沿用前述通過結果。

```text
python -m unittest discover -s tests -k tree -k preset_path -k DistributionTests -v
```

可攜性測試實際建立 ZIP、解壓到獨立暫存位置，並從另一個工作目錄執行解壓出的工具，成功查到固定版本的交易範例。這是本地解壓與工具執行證據，不是某個 agent 已安裝或啟用 skill 的證據。

```text
python scripts/validate_repository.py
```

檢查 skill 入口與 metadata 必要欄位、UTF-8、Python 語法、本地連結、skill 內相對路徑、授權副本、來源雜湊形狀、索引計數與版本連結，以及私人機器路徑。六個 XS 範例僅檢查類型註解，沒有當成 XS 語法分析器。

另以環境提供的 skill-creator `quick_validate.py` 檢查入口，結果為 `Skill is valid!`；此工具在 Windows 使用 `python -X utf8` 執行。UI YAML 另經 YAML parser 讀取，確認各欄位為字串、提示含 skill 名稱，短說明為 36 字。此 parser 僅供維護驗證，不是工具執行相依。

```text
python scripts/build_package.py --output dist/xq-xs-community-v0.1.0.zip
```

v0.1.0 發佈檔案為 `dist/xq-xs-community-v0.1.0.zip`；旁附 SHA-256 檔，摘要以實際建置檔為準。建置輸出不納入 source commit，可由已提交來源重建。

本次 ZIP 為 **144,117 bytes、22 個檔案**；逐一比對封裝內容與當前來源相同，CRC 與 SHA-256 核對通過，並實際解壓執行其中的離線查找工具。本次產物的 SHA-256：

```text
0615be1814d0969421e2ba927866c48c131d224a08d34921dd9d66d9cc81dc52
```

來源與 ZIP 均檢查私人機器路徑；另掃描常見 access token、private key 與 URL 內嵌憑證模式，未命中。這是對本次輸出的檢查結果，不是完整秘密資訊偵測的保證。

README 經 GitHub Markdown API 渲染，檢查標題、表格、封面與徽章排列；另以本機 headless Chrome 檢視桌機版面。封面 PNG 的格式、尺寸與檔案身分已核對，生成方式與完整提示見 [封面說明](../assets/README.md)。

## 官方來源查證

實際讀取 XSHelp 首頁與核心 API 頁，包括 `GetField`、`GetQuote`、`Input`、`Array`、`OutputField`、`SetBarMode`、`SetTotalBar`、`SetBackBar`、`Rank`、`SetPosition`、`Filled` 與 `CancelAllOrders` 的說明／搜尋結果；另讀官方欄位對位教學。

實際讀取 upstream commit `d15a4157ccb2c439b3633dec200808924a7f83a7` 的未截斷檔案樹，並查看代表性的數值／布林函數、警示、選股、指標、跨頻率函數與交易時序／刪單範例。這支持已記錄的語義校正，不代表全部 1,419 支腳本均經內容審查。

官方直達頁與固定版本連結見 [來源地圖](../xq-xs/references/source-map.md)。所有 1,455 筆 help／文章識別紀錄的 URL 並未逐一連線驗證；83 筆只有搜尋連結。索引整併日期不等於 API 的現行查證日期。

## 2026-10-21 當時尚未執行

- 在 XQ 編輯器編譯六個原創 XS 範例。
- 對指定商品、頻率與期間進行 XQ 歷史執行或回測。
- 驗證雷達通知設定、模擬成交、帳戶庫存或實盤行為。
- 在其他作業系統或 Python 3.10 上執行工具測試。
- 安裝到個人 agent skills 目錄，或進行模型端的自然選用／多輪使用評估。

本紀錄描述本地套件與工具的驗證。GitHub 發佈狀態請查 [社群專案 Releases](https://github.com/pypysuper-og/xq-xs-skill-community/releases)，與 XQ runtime 驗證分開判斷。

因此可以判定本版本的本地套件與查找工具已依上述範圍檢查，不能據此宣稱 XS 程式可編譯、策略已通過回測、agent 使用情境皆已驗證或可直接實盤。
