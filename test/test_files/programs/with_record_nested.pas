program with_record_nested;

type
  Point = record
    x, y : Integer;
  end;

  Box = record
    topLeft : Point;
  end;

var
  b : Box;

begin
  with b.topLeft do
  begin
    x := 9;
    y := 8;
  end;
  writeln(b.topLeft.x);
  writeln(b.topLeft.y);
end.
