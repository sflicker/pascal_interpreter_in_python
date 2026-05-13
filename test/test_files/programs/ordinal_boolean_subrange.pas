program OrdinalBooleanSubrange;

type
  Small = 1..3;

var
  flag: BOOLEAN;
  n: Small;

begin
  flag := SUCC(FALSE);
  WRITELN(flag);
  flag := PRED(TRUE);
  WRITELN(flag);

  n := 2;
  WRITELN(PRED(n));
  WRITELN(SUCC(n));
end.
