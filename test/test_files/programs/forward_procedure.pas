PROGRAM ForwardProcedure;

PROCEDURE PrintValue(value: INTEGER); FORWARD;

PROCEDURE Run;
BEGIN
  PrintValue(42);
END;

PROCEDURE PrintValue(value: INTEGER);
BEGIN
  WRITELN(value);
END;

BEGIN
  Run;
END.
