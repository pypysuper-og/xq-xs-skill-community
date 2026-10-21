{@type:function}
// 原創示範；函數須命名為 XSChangePercent。未在 XQ 編譯或執行。
SetBarMode(1);
Input: CurrentValue(NumericSeries), BaseValue(NumericSeries);

if BaseValue = 0 then
    RaiseRunTimeError("比較基準不可為零")
else
    XSChangePercent = 100 * (CurrentValue / BaseValue - 1);
