PROGRAM SetChar;
VAR
  letters: SET OF CHAR;
BEGIN
  letters := ['a'..'c'];
  WRITELN('b' IN letters);
  WRITELN('z' IN letters);
END.
