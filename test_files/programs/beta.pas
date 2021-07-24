program Main;
{ output should be 70\n30\n }
procedure Alpha(a : integer; b : integer);
var x : integer;

  procedure Beta(a : integer; b: integer);
  var x : integer;
  begin
      x := a * 10 + b * 2;
      { output should be 70 }
      writeln(x);
  end;

begin
    x := (a + b) * 2;
    Beta(5, 10);
    { output should be 30 }
    writeln(x);
end;

begin { main }
    Alpha(3 + 5, 7);
end. { Main }