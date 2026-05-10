program goto_loop;

label 10, 20;

var n : Integer;
begin
  n := 0;
10:
  n := n + 1;
  if n < 3 then
    goto 10;
20:
  writeln(n);
end.
