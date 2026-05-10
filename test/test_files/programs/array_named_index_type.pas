PROGRAM ArrayNamedIndexType;
CONST
  First = 1;
  Last = 3;
TYPE
  Index = First..Last;
VAR
  values: ARRAY [Index] OF INTEGER;
BEGIN
  values[1] := 5;
  values[2] := 7;
  values[3] := values[1] + values[2];
  WRITELN(values[3]);
END.
