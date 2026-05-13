program LibraryIncDecUpcaseValStr;

var
  n: INTEGER;
  r: REAL;
  code: INTEGER;
  word: STRING;
  ch: CHAR;

begin
  n := 10;
  INC(n);
  INC(n, 4);
  DEC(n, 3);
  WRITELN(n);

  ch := UPCASE('q');
  word := UPCASE("pascal");
  WRITELN(ch);
  WRITELN(word);

  VAL("42", n, code);
  WRITELN(n);
  WRITELN(code);

  VAL("3.5", r, code);
  WRITELN(r:1:1);
  WRITELN(code);

  VAL("bad", n, code);
  WRITELN(code);

  STR(n, word);
  WRITELN(word);
end.
