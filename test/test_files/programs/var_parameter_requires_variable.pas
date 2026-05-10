program var_parameter_requires_variable;

var
  a : Integer;

procedure increment(var value : Integer);
begin
  value := value + 1;
end;

begin
  a := 10;
  increment(a + 1);
end.
