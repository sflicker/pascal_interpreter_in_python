program functionargs_too_few;

var n : Integer;

function add(a : Integer; b : Integer) : Integer;
begin
  add := a + b;
end;

begin
  n := add(1);
end.
