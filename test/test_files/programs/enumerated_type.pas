PROGRAM EnumeratedType;
TYPE
  Direction = (North, East, South, West);
VAR
  d: Direction;
BEGIN
  d := East;
  WRITELN(ORD(d));
  d := SUCC(d);

  IF d > East THEN
    WRITELN(ORD(d));

  CASE d OF
    North: WRITELN(0);
    South: WRITELN(22);
    West: WRITELN(33);
  END;
END.
