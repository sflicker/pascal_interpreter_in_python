program array_downto;

var arr : array [1..3] of Integer;
    i : Integer;

begin
  for i := 3 downto 1 do
    arr[i] := i * 2;
  writeln(arr[1]);
  writeln(arr[2]);
  writeln(arr[3]);
end.
