PROGRAM StringConcatDeleteInsert;
VAR
  value: STRING;
BEGIN
  value := CONCAT('Pas', 'cal', ' ', 'Rocks');
  WRITELN(value);
  DELETE(value, 7, 6);
  WRITELN(value);
  INSERT(' rules', value, 7);
  WRITELN(value);
END.
