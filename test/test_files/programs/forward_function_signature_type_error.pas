PROGRAM ForwardFunctionSignatureTypeError;

FUNCTION Convert(value: INTEGER): INTEGER; FORWARD;

FUNCTION Convert(value: INTEGER): REAL;
BEGIN
  Convert := value;
END;

BEGIN
  WRITELN(Convert(1));
END.
