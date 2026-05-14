program CaseOverlappingRangeLabel;

var
  ch: CHAR;

begin
  ch := 'd';
  CASE ch OF
    'a'..'f': WRITELN('first');
    'd'..'z': WRITELN('second');
  END;
end.
