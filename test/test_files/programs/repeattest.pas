program repeattest;

var n : Integer;
begin
  n := 0;
  repeat
    n := n + 1;
  until n = 5;
  writeln(n);
end.
