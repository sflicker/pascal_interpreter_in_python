PROGRAM FileAppend;
VAR
  f: TEXT;
BEGIN
  ASSIGN(f, 'log.txt');
  APPEND(f);
  WRITELN(f, 'second');
  CLOSE(f);
END.
