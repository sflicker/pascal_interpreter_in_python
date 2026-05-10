program record_basic;

type
  Person = record
    name : String;
    age : Integer;
  end;

var
  p : Person;

begin
  p.name := "Ada";
  p.age := 36;
  writeln(p.name);
  writeln(p.age);
end.
