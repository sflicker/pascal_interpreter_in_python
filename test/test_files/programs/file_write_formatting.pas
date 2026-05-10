PROGRAM FileWriteFormatting;
VAR
  f: TEXT;
BEGIN
  ASSIGN(f, 'formatted.txt');
  REWRITE(f);
  WRITELN(f, '>', 5:3, '<');
  WRITELN(f, '>', 2.5:5:1, '<');
  CLOSE(f);
END.
