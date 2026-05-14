program TypedFileInteger;

var
  values: FILE OF INTEGER;
  n: INTEGER;
  total: INTEGER;

begin
  ASSIGN(values, 'numbers.dat');
  REWRITE(values);
  n := 10;
  WRITE(values, n);
  n := 20;
  WRITE(values, n);
  CLOSE(values);

  total := 0;
  RESET(values);
  WHILE NOT EOF(values) DO
  BEGIN
    READ(values, n);
    total := total + n;
  END;
  CLOSE(values);

  WRITELN(total);
end.
