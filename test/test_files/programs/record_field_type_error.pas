program record_field_type_error;

type
  Person = record
    age : Integer;
  end;

var
  p : Person;

begin
  p.age := "old";
end.
