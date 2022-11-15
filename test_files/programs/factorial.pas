program factorial;


function fact(f : integer) : integer;
begin
  writeln('entering fact function, fn=', f);
  if f < 3 then fact := f
  else
    begin
      fact := f*fact(f-1);
      writeln(fact: 5);
    end;
  writeln('leaving fact function, fn=', f, ',  fact=',fact);
end;

begin
  writeln(fact(4));
end.