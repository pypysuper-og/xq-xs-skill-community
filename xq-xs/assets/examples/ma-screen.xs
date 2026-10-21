{@type:filter}
// 原創示範；未在 XQ 編譯或執行。選股請選支援的日或更長頻率。
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
Ret = 0;
if CurrentBar > SlowLength then begin
    if FastMA crosses over SlowMA then Ret = 1;
    OutputField(1, FastMA, 2, "短期均線");
    OutputField(2, SlowMA, 2, "長期均線");
end;
