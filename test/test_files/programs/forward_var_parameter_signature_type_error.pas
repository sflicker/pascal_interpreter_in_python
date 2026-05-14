PROGRAM ForwardVarParameterSignatureTypeError;

VAR
  n: INTEGER;

PROCEDURE Touch(VAR value: INTEGER); FORWARD;

PROCEDURE Touch(value: INTEGER);
BEGIN
  value := value + 1;
END;

BEGIN
  n := 1;
  Touch(n);
END.
