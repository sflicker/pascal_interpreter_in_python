program casetest;

var grade : Integer;
    letter : String;
begin
  grade := 2;
  case grade of
    1: letter := "A";
    2: letter := "B";
    3: letter := "C";
  end;
  writeln(letter);
end.
