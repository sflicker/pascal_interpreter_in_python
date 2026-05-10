PROGRAM ArrayConstIndexBoundsError;
CONST
  Low = 2;
  High = 4;
VAR
  values: ARRAY [Low..High] OF INTEGER;
BEGIN
  values[1] := 10;
END.
