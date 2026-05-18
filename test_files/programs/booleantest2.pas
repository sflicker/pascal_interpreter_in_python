program booleantest2;

var
	a, b, c : boolean;
begin
	a := true;
	b := false;
  c := a + b;   { this should be invalid }
  writeln(a, b, c);
end.

