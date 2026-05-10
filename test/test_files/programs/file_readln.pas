PROGRAM FileReadln;
VAR
  f: TEXT;
  name: STRING;
  count, score: INTEGER;
BEGIN
  ASSIGN(f, 'scores.txt');
  RESET(f);
  READLN(f, name, count);
  READ(f, score);
  CLOSE(f);

  WRITELN(name);
  WRITELN(count + score);
END.
