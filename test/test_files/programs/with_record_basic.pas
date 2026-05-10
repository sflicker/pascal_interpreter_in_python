program with_record_basic;

type
  Person = record
    name : String;
    age : Integer;
  end;

var
  p : Person;

begin
  with p do
  begin
    name := "Grace";
    age := 37;
    writeln(name);
    writeln(age);
  end;
  writeln(p.name);
  writeln(p.age);
end.
