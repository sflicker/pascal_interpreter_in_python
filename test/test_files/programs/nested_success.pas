program nested_success;

var total : Integer;

procedure Outer(a : Integer);
var local : Integer;

  procedure Inner(b : Integer);
  begin
    total := total + a + b + local;
  end;

begin
  local := 3;
  Inner(4);
end;

begin
  total := 1;
  Outer(2);
  writeln(total);
end.
