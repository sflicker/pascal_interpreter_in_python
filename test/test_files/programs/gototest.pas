program gototest;

label 100;

var n : Integer;
begin
  n := 1;
  goto 100;
  n := 99;
100:
  writeln(n);
end.
