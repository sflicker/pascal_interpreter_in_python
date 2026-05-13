program CaseRangeLabelTypeError;

var
  n: INTEGER;

begin
  n := 1;
  CASE n OF
    'a'..'z': WRITELN('bad');
  END;
end.
