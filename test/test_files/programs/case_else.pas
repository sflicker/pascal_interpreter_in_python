program case_else;

var grade : Integer;
    letter : String;
begin
  grade := 9;
  case grade of
    1: letter := 'A';
    2: letter := 'B';
  else
    letter := 'F';
  end;
  writeln(letter);
end.
