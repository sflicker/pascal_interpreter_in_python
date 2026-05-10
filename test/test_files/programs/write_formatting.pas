PROGRAM WriteFormatting;
VAR
  n: INTEGER;
  r: REAL;
BEGIN
  n := 7;
  r := 3.14159;
  WRITELN('>', n:4, '<');
  WRITELN('>', r:8:2, '<');
  WRITELN('>', 'Ada':6, '<');
  WRITELN('>', 12.5:6:0, '<');
END.
