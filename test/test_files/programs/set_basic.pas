PROGRAM SetBasic;
TYPE
  Digit = 0..9;
VAR
  odds, evens, small: SET OF Digit;
BEGIN
  odds := [1, 3, 5];
  evens := [2, 4, 6];
  small := [1..4];

  IF 3 IN odds THEN
    WRITELN('odd');

  IF 5 IN small THEN
    WRITELN('bad')
  ELSE
    WRITELN('small');

  odds := odds + evens;
  small := small * odds;
  odds := odds - [6];

  WRITELN(2 IN odds);
  WRITELN(6 IN odds);
  WRITELN(4 IN small);
END.
