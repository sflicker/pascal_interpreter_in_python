program Main;

procedure Alpha(a : integer; b : integer);
var x : integer;

  procedure Beta(a : integer; b: integer);
  var x : integer;
  begin
      x := a * 10 + b * 2;
  end;

begin
    x := (a + b) * 2;
    Beta(5, 10);
end;

begin { main }
    Alpha(3 + 5, 7);
end. { Main }