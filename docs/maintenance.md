# 維護、驗證與套件建置

## 日常修改

`xq-xs/` 是可安裝 skill 的唯一來源，根目錄工具只負責維護。修改與當前需求相符的參考文件，不複製第二個 skill 入口，也不把整份手冊放進 `SKILL.md`。

更新 API 說明時，核對正式頁面、腳本類型、商品與頻率；更新交易語義時，同時查看代表性的官方交易範例。頁面名稱正確或語法能高亮，都不能取代編譯與執行證據。

原創內容、索引與外部內容分開維護。新增第三方原文或程式前，先確認其授權；目前套件只附識別索引與原創摘要／範例。

## 重建索引

一般使用與打包不需要原始快照。只有重建索引時才需要八份文件：

```text
內建.md
系統.md
報價.md
資料.md
選股.md
關鍵字.md
XS語法運用.md
all_documentation.md
```

重建器僅讀取識別名稱、分類、URL 與條目標題，忽略說明與程式本體，並保留輸入雜湊與計數。來源格式改變、命名空間不認識或沒有有效條目時回報錯誤；不要為了通過而靜默略過整份文件。

另以 GitHub connector 或唯讀 API 取得某一**完整 commit SHA** 的遞迴樹。先確認 commit 的 `commit.tree.sha` 與樹回應的 `sha` 相同，且 `truncated` 是 `false`。例如 API 形狀：

```text
GET https://api.github.com/repos/sysjust-xq/XScript_Preset/commits/<full-commit-sha>
GET https://api.github.com/repos/sysjust-xq/XScript_Preset/git/trees/<tree-object-sha>?recursive=1
```

將樹的 JSON 存成 UTF-8。以下參數中的路徑是維護者提供的輸入位置，不應將私人完整路徑寫進公開文件或索引：

```text
python scripts/build_catalogs.py --reference-dir <snapshot-folder> --preset-tree <tree.json> --preset-commit <full-commit-sha> --assembled-on <YYYY-MM-DD>
```

預設輸出為 `xq-xs/data/`。可用 `--output-dir` 先輸出到另一個建置目錄比較。`assembled_on` 只代表本次整理日期，不能提升舊快照的新鮮度；`--preset-commit` 需與取得樹時的版本一致。重建器拒絕將 commit 別名誤記為 tree object，仍由維護者核對 commit 與實際 tree SHA 的對應；它不自行連線驗證。

只要網址來自原始欄位，便保留其名稱／分類；沒有直達網址時產生官方搜尋連結。不要把猜測分類的網址標成已驗證。去重須以命名空間區隔資料、報價與選股欄位。

重建後檢視新增／刪除名稱、來源雜湊、搜尋連結數與五類官方腳本數量，按結果更新 README 與整併文件。不要把更新索引寫成「所有 API 均已驗證」。

## 最小驗證

在專案根目錄用 Python 3.10+ 執行：

```text
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

測試覆蓋多行抓取表格、關鍵字 article／api URL、命名空間去重、缺網址的搜尋退路、完整樹檢查、URL 編碼、查找排序／結束碼，以及抽離 ZIP 後的工具使用。

套件檢查會檢查 UTF-8、skill 必要欄位、Python 語法、本地 Markdown 連結、安裝資料夾內連結、索引來源／版本一致性與私人機器路徑。它不會逐一連線驗證外部網址，也不會解析或編譯 XS。公開發布前仍須讀一遍變更文案，檢查真實憑證與不應公開的材料，而非只依賴掃描器。

可額外使用目標 agent 提供的 skill frontmatter validator；它屬於該環境工具，並非套件執行相依。若該工具採系統預設編碼讀檔，Windows 可用 `python -X utf8` 執行。UI metadata 為可選的 `agents/openai.yaml`，沒有指定模型、provider 或強制外部服務。

## 建置與安裝查核

```text
python scripts/build_package.py
```

輸出 `dist/xq-xs.zip` 和 `dist/xq-xs.zip.sha256`；ZIP 內只有一個頂層 `xq-xs/`。打包器只允許 skill 入口、授權與明列資源目錄；拒絕未知檔案及符號連結，略過 Python cache。其建置輸出不加入 Git。

解壓後，可從另一個工作目錄執行解壓出的 `xq-xs/scripts/lookup.py`，確認工具是依自身位置讀資料。測試會涵蓋這個可攜性，不會寫入個人 skills 目錄。

實際安裝時保留整個 skill 目錄與相對路徑；若已有同名 skill，先檢視差異再選更新方式。套件驗證不代表 agent 已載入安裝，也不代表 XS 已編譯。
