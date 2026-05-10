PROGRAM ArrayConstIndexBounds;
CONST
  Low = 2;
  High = 4;
VAR
  values: ARRAY [Low..High] OF INTEGER;
BEGIN
  values[2] := 20;
  values[3] := 30;
  values[4] := values[2] + values[3];
  WRITELN(values[4]);
END.
