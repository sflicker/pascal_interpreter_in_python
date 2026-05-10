program factorial;


function fact(f : integer) : integer;
begin
  if f < 3 then fact := f
  else
    fact := f*fact(f-1);
end;

begin
  writeln(fact(4));
end.
