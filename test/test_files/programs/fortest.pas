program fortest;

var i, count : Integer;

begin
  count := 0;
  for i := 1 to 10 do
  begin
    count := count + 1;
  end;
  writeln(count);

  for i := 10 downto 1 do
  begin
    count:= count + 1;
  end;
  writeln(count);
  writeln(i);
end.