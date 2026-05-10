PROGRAM FileEofEoln;
VAR
  f: TEXT;
  value: INTEGER;
  total: INTEGER;
BEGIN
  total := 0;
  ASSIGN(f, 'numbers.txt');
  RESET(f);

  READ(f, value);
  WRITELN(EOLN(f));
  total := total + value;
  READ(f, value);
  WRITELN(EOLN(f));
  total := total + value;
  READLN(f);

  WHILE NOT EOF(f) DO
  BEGIN
    READLN(f, value);
    total := total + value;
  END;

  WRITELN(EOF(f));
  WRITELN(total);
  CLOSE(f);
END.
