# 官方 VS Code 語法高亮的參考方式

需要設定 XS 編輯器、辨識詞彙或解釋顏色時，使用這份參考。實際語法、型別與腳本支援仍以 XSHelp 及指定版本的 XQ 編譯結果確認。

## 固定來源

[XS Script Language 擴充套件](https://marketplace.visualstudio.com/items?itemName=sysjust-xq.xs) 的 publisher 是 `sysjust-xq`。本套件於 2026-11-09 查閱其 [官方原始碼](https://github.com/sysjust-xq/vscode-xs/tree/c6101a57676990160de656171bd72638d5758102)，固定到 2023-04-26 的 commit `c6101a57676990160de656171bd72638d5758102`，extension version `1.0.2`。

隨附 [TextMate grammar](../assets/editor/xs.tmLanguage.json)、[語言設定](../assets/editor/language-configuration.json) 與 [來源識別](../assets/editor/source.json)。上游 package 的貢獻是語言與高亮設定；這個版本沒有附編譯器、language server 或 snippets。使用者不必安裝 VS Code 才能使用本 Skill。

## 可以取用的規則

| 原始設定 | 寫作／編輯時的用途 | 不可延伸的結論 |
|---|---|---|
| `scopeName: source.xs` | 對 XS 檔套用 TextMate 顏色 | 不能作為檔案已編譯的標記 |
| `//`、可遞迴的 `{ ... }` 註解規則 | 區分註解與程式碼；閱讀 type comment | 不能把 `Begin ... End` 當成註解 |
| `(?i)` 關鍵字／函數比對 | 以不分大小寫方式辨識已列詞彙 | 沒列入不表示 XS 不支援 |
| 宣告、流程、運算子、builtin／system function 分組 | 編輯器分類與名稱查找線索 | 不能從顏色推斷參數、型別或可呼叫情境 |
| `Value`／`Condition`、OHLCV、`q_` 欄位分組 | 提醒預設變數、序列與報價來源的差別 | 正規表示式不是完整有效名稱清單 |
| 雙引號字串與十進位／科學記號規則 | 閱讀數字、字串及高亮範圍 | 不能取代完整 lexer、parser 或字串跳脫規格 |
| 括號、註解切換與引號自動補齊 | 設定編輯便利功能 | 自動補齊單引號不證明 XS 接受單引號字串 |

## 已辨識的限制

- 控制詞正規表示式有 `TrueFalseSimpleVar` 這個合併項目與重複的 Cross 詞彙；不要據此創造一個 XS 宣告型別。
- 運算子 regex 沒有完整列出所有運算子；不能拿它當合法運算子的白名單。
- 預設變數 regex 的分組與邊界並不一致，`Value[0-9]{1,3}` 也不能證明編譯器允許的變數編號上限。
- 原始 grammar 的常數 scope 是 `variable.constant.xs`。以檔案內容為準，不以套件介紹中的拼字代替實際設定。
- 該固定版本列有 `SetBarBack`，沒有 `SetBackBar`；本專案的四種原創腳本使用 `SetBackBar`，已於 XQ 個人版 `3.20.04 261006` 編譯通過。這是「沒有高亮仍可編譯」的具體反例，不代表兩個名稱可任意互換。

因此採三層使用方式：高亮協助閱讀，XSHelp 確認 API 與限制，[桌面編譯工具](desktop-compile.md) 確認該環境是否接受程式。編譯成功仍不驗證資料、策略或成交行為。

兩份上游檔案依 MIT 收錄；完整署名與條款見 [第三方聲明](../THIRD_PARTY_NOTICES.md)。不要直接修改隨附的固定來源來宣稱已修正上游；如需衍生編輯器設定，另外標示改動與來源版本。
