program procedureargs_too_many;

procedure show(a : Integer; b : Integer);
begin
  writeln(a);
end;

begin
  show(1, 2, 3);
end.
