PROGRAM ForwardProcedureSignatureTypeError;

PROCEDURE Show(value: INTEGER); FORWARD;

PROCEDURE Show(value: REAL);
BEGIN
  WRITELN(value);
END;

BEGIN
  Show(1);
END.
