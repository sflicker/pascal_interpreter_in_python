PROGRAM ForwardFunction;

FUNCTION AddOne(value: INTEGER): INTEGER; FORWARD;

FUNCTION AddOne(value: INTEGER): INTEGER;
BEGIN
  AddOne := value + 1;
END;

BEGIN
  WRITELN(AddOne(9));
END.
