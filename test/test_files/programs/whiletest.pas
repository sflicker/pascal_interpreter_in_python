program whiletest;
  var
    n, count : integer;
BEGIN
   n := 10;
   count := 0;
   while n > 0 do
   begin
      count := count + 1;
      n := n - 1
   end;
   writeln(n);
   writeln(count);
end.
