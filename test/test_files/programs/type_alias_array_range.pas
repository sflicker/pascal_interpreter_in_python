program type_alias_array_range;

type
  Range = 1..3;

var
  values : array [Range] of Integer;

begin
  values[1] := 10;
  values[3] := 30;
  writeln(values[1]);
  writeln(values[3]);
end.
