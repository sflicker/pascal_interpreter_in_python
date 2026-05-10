program var_parameter_swap;

var
  a, b : Integer;

procedure swap(var left, right : Integer);
var
  temp : Integer;
begin
  temp := left;
  left := right;
  right := temp;
end;

begin
  a := 10;
  b := 20;
  swap(a, b);
  writeln(a);
  writeln(b);
end.
