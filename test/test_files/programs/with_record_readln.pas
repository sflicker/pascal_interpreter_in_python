program with_record_readln;

type
  Point = record
    xcoord, ycoord : Real;
  end;

var
  point1 : Point;
  distance : Real;

begin
  with point1 do
  begin
    readln(xcoord);
    readln(ycoord);
    distance := sqrt(sqr(xcoord) + sqr(ycoord));
    writeln(distance);
  end;
end.
