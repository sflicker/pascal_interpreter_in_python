program builtin_abs_sqr_odd;

var
  a, b, c : Integer;
  flag1, flag2 : Boolean;

begin
  a := abs(-5);
  b := sqr(7);
  c := abs(3 - 10);
  flag1 := odd(7);
  flag2 := odd(8);
  writeln(a);
  writeln(b);
  writeln(c);
  writeln(flag1);
  writeln(flag2);
end.
