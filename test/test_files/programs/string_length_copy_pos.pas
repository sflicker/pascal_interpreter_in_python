PROGRAM StringLengthCopyPos;
VAR
  word: STRING;
BEGIN
  word := 'Pascal';
  WRITELN(LENGTH(word));
  WRITELN(COPY(word, 2, 3));
  WRITELN(POS('cal', word));
  WRITELN(POS('x', word));
END.
