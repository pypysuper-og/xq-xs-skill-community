{@type:sensor}
// 原創示範；未在 XQ 編譯或執行。通知次數另依雷達設定與去重需求核對。
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
end;
