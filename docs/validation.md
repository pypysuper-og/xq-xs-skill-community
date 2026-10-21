# 驗證紀錄

驗證日期：**2026-10-21**。執行環境：Windows、Python **3.13.5**。範圍為 skill 套件、索引與工具；不包含 XQ runtime。

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
python scripts/build_package.py
```

發佈檔案為 `dist/xq-xs.zip`；旁附 SHA-256 檔，摘要以實際建置檔為準。建置輸出不納入 source commit，可由已提交來源重建。

本次 ZIP 為 **143,884 bytes、22 個檔案**；逐一比對封裝內容與當前來源相同，CRC 與 SHA-256 核對通過。本次產物的 SHA-256：

```text
a76b6adb583bc1f19e914224800284f1ebb63bc2b55f2042713cf5e218882e17
```

來源與 ZIP 均檢查私人機器路徑；另掃描常見 access token、private key 與 URL 內嵌憑證模式，未命中。這是對本次輸出的檢查結果，不是完整秘密資訊偵測的保證。

## 官方來源查證

實際讀取 XSHelp 首頁與核心 API 頁，包括 `GetField`、`GetQuote`、`Input`、`Array`、`OutputField`、`SetBarMode`、`SetTotalBar`、`SetBackBar`、`Rank`、`SetPosition`、`Filled` 與 `CancelAllOrders` 的說明／搜尋結果；另讀官方欄位對位教學。

實際讀取 upstream commit `d15a4157ccb2c439b3633dec200808924a7f83a7` 的未截斷檔案樹，並查看代表性的數值／布林函數、警示、選股、指標、跨頻率函數與交易時序／刪單範例。這支持已記錄的語義校正，不代表全部 1,419 支腳本均經內容審查。

官方直達頁與固定版本連結見 [來源地圖](../xq-xs/references/source-map.md)。所有 1,455 筆 help／文章識別紀錄的 URL 並未逐一連線驗證；83 筆只有搜尋連結。索引整併日期不等於 API 的現行查證日期。

## 尚未執行

- 在 XQ 編輯器編譯六個原創 XS 範例。
- 對指定商品、頻率與期間進行 XQ 歷史執行或回測。
- 驗證雷達通知設定、模擬成交、帳戶庫存或實盤行為。
- 在其他作業系統或 Python 3.10 上執行工具測試。
- 安裝到個人 agent skills 目錄，或進行模型端的自然選用／多輪使用評估。
- 遠端發布、push 或建立 release。

因此可以判定本版本的本地套件與查找工具已依上述範圍檢查，不能據此宣稱 XS 程式可編譯、策略已通過回測、agent 使用情境皆已驗證或可直接實盤。
