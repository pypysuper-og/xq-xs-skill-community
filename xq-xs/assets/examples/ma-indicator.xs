{@type:indicator}
// 原創示範；未在 XQ 編譯或執行。期數單位為目前頻率的 bar。
Input: FastLength(5, "短期期數"), SlowLength(20, "長期期數");
Variable: FastMA(0), SlowMA(0);

if FastLength < 1 or SlowLength <= FastLength or SlowLength > 250 then
    RaiseRunTimeError("需滿足 1 <= 短期 < 長期 <= 250");
if FastLength <> IntPortion(FastLength) or SlowLength <> IntPortion(SlowLength) then
    RaiseRunTimeError("期數須為整數");
SetTotalBar(300);
SetBackBar(300);

FastMA = Average(Close, FastLength);
SlowMA = Average(Close, SlowLength);
if CurrentBar > SlowLength then begin
    Plot1(FastMA, "短期均線");
    Plot2(SlowMA, "長期均線");
end else begin
    NoPlot(1);
    NoPlot(2);
end;
