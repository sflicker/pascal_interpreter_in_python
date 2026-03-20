program main;
  var x,y: integer;

  procedure Alpha(a: integer);
    var y : integer;
  begin
    a := 2;
    x := 5;
    y := 1;
    x := a + x + y;
    writeln(a);
    writeln(x);
    writeln(y);
  end;

begin
    x := 3;
    y := 5;
    Alpha(5);
    writeln(x);
    writeln(y);
end.