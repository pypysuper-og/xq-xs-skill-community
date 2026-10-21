{@type:autotrade}
// 原創教學骨架；預設關閉交易指令。未在 XQ 編譯、回測或執行。
Input: EnableOrders(false, "啟用交易指令"),
       FastLength(5, "短期期數"), SlowLength(20, "長期期數"),
       TargetLots(1, "多單目標單位");
Variable: FastMA(0), SlowMA(0), EntrySignal(false), ExitSignal(false),
          DesiredPosition(0), RequestOrder(false);

if FastLength < 1 or SlowLength <= FastLength or SlowLength > 250 then
    RaiseRunTimeError("需滿足 1 <= 短期 < 長期 <= 250");
if FastLength <> IntPortion(FastLength) or SlowLength <> IntPortion(SlowLength) then
    RaiseRunTimeError("期數須為整數");
if TargetLots < 1 or TargetLots <> IntPortion(TargetLots) then
    RaiseRunTimeError("目標單位須為正整數");
SetTotalBar(300);
SetBackBar(300);

FastMA = Average(Close, FastLength);
SlowMA = Average(Close, SlowLength);
EntrySignal = FastMA crosses over SlowMA;
ExitSignal = FastMA crosses under SlowMA;
DesiredPosition = Position;
RequestOrder = false;

if EnableOrders and CurrentBar > SlowLength then begin
    if Position < 0 or Filled < 0 then
        RaiseRunTimeError("此教學範例只處理多單策略部位");

    // 退出優先；未成交與部分成交的進場也可改為目標空手。
    if (Position > 0 or Filled > 0) and ExitSignal then begin
        DesiredPosition = 0;
        RequestOrder = true;
    end else if Position = 0 and Filled = 0 and EntrySignal then begin
        DesiredPosition = TargetLots;
        RequestOrder = true;
    end;

    // 每次洗價至多一個指令。Close 是指定限價，並不保證成交。
    if RequestOrder then SetPosition(DesiredPosition, Close);
end;
