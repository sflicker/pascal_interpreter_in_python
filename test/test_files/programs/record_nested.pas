program record_nested;

type
  Point = record
    x, y : Integer;
  end;

  Box = record
    topLeft : Point;
    labelText : String;
  end;

var
  b : Box;

begin
  b.topLeft.x := 3;
  b.topLeft.y := 4;
  b.labelText := "origin";
  writeln(b.topLeft.x);
  writeln(b.topLeft.y);
  writeln(b.labelText);
end.
