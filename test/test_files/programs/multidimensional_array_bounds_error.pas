PROGRAM MultidimensionalArrayBoundsError;
VAR
  grid: ARRAY [1..2, 1..3] OF INTEGER;
BEGIN
  grid[1, 4] := 10;
END.
