program arraytest1;

var arr : array [1..10] of Integer;
    i : Integer;

begin
  for i := 1 to 10 do
  begin
    arr[i] := i;
    writeln('i=',i);
    writeln('arr[i]=', arr[i]);
    writeln;
  end;
end.