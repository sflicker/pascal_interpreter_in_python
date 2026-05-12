program BuiltinStandardConstants;

const
  Lowest = MININT;
  Circle = PI;

var
  low: INTEGER;
  area: REAL;

begin
  low := MININT;
  area := PI * 2.0;
  writeln(low);
  writeln(Lowest);
  writeln(Circle:1:2);
  writeln(area:1:2);
end.
