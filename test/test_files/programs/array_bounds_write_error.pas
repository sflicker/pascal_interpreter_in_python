program array_bounds_write_error;

var
  values : array [2..4] of Integer;

begin
  values[1] := 10;
end.
