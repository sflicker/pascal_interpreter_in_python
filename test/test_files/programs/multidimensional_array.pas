PROGRAM MultidimensionalArray;
VAR
  grid: ARRAY [1..2, 1..3] OF INTEGER;
  i, j: INTEGER;
  total: INTEGER;
BEGIN
  total := 0;
  FOR i := 1 TO 2 DO
    FOR j := 1 TO 3 DO
    BEGIN
      grid[i, j] := i * 10 + j;
      total := total + grid[i, j];
    END;

  WRITELN(grid[2, 3]);
  WRITELN(total);
END.
