{@type:function_bool}
// 原創示範；函數須命名為 XSAboveThreshold。未在 XQ 編譯或執行。
SetBarMode(1);
Input: PriceSeries(NumericSeries), Threshold(NumericSimple);

XSAboveThreshold = PriceSeries > Threshold;
