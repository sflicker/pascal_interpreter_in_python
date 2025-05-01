program factorial;


function fact(f : integer) : integer;
var result : integer;
begin
  writeln('entering fact function, fn=', f);
  if f < 3 then result := f
  else
    begin
      result := f*fact(f-1);
      writeln(result: 5);
    end;
  writeln('leaving fact function, fn=', f, ',  result=',result);
  fact := result;
end;

begin
  writeln(fact(4));
end.