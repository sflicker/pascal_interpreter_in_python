program case_multilabel;

var n : Integer;
    labeltext : String;
begin
  n := 4;
  case n of
    1, 3, 5: labeltext := 'odd';
    2, 4, 6: labeltext := 'even';
  else
    labeltext := 'unknown';
  end;
  writeln(labeltext);
end.
