program CaseRangeLabels;

type
  Direction = (North, East, South, West);

var
  n: INTEGER;
  ch: CHAR;
  heading: Direction;

begin
  n := 4;
  CASE n OF
    1..3: WRITELN('small');
    4..6: WRITELN('medium');
  ELSE
    WRITELN('large');
  END;

  ch := 'c';
  CASE ch OF
    'a'..'f': WRITELN('early');
    'g'..'z': WRITELN('late');
  END;

  heading := South;
  CASE heading OF
    North..East: WRITELN('up');
    South..West: WRITELN('down');
  END;
end.
