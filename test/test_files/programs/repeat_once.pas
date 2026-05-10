program repeat_once;

var n : Integer;
begin
  n := 10;
  repeat
    n := n + 1;
  until n > 0;
  writeln(n);
end.
