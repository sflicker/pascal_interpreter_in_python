program array_bounds_read_error;

var
  values : array [2..4] of Integer;
  a : Integer;

begin
  a := values[5];
end.
