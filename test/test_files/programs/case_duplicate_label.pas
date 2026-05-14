program CaseDuplicateLabel;

var
  n: INTEGER;

begin
  n := 2;
  CASE n OF
    1, 2: WRITELN('first');
    2: WRITELN('second');
  END;
end.
