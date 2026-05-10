PROGRAM ADD;

function Add(a, b:integer): integer;
begin
  Add := a + b;
end;

var result: integer;

begin
  result := Add(3,4);
  writeln('Result', result);
  writeln;
end.

