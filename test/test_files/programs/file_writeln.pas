PROGRAM FileWriteln;
VAR
  f: TEXT;
BEGIN
  ASSIGN(f, 'report.txt');
  REWRITE(f);
  WRITE(f, 'Ada');
  WRITELN(f, ' Lovelace');
  WRITELN(f, 42);
  CLOSE(f);

  WRITELN('done');
END.
