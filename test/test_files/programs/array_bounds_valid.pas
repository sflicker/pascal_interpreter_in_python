program array_bounds_valid;

var
  values : array [2..4] of Integer;

begin
  values[2] := 20;
  values[4] := 40;
  writeln(values[2]);
  writeln(values[4]);
end.
