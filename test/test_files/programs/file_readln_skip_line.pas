PROGRAM FileReadlnSkipLine;
VAR
  f: TEXT;
  value: INTEGER;
BEGIN
  ASSIGN(f, 'numbers.txt');
  RESET(f);
  READLN(f);
  READLN(f, value);
  CLOSE(f);

  WRITELN(value);
END.
