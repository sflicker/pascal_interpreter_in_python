program procedureargtest;

type intprocedure = procedure(a: integer);

procedure writeint(a: integer);
begin
  writeln(a);
end;

procedure test1( afunc:  intprocedure );
begin
  afunc(1);
end;

begin
  test1(@writeint);
end.

