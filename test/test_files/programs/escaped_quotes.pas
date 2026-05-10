PROGRAM EscapedQuotes;
VAR
  quote: CHAR;
BEGIN
  quote := '''';
  WRITELN('Ada''s note');
  WRITELN("She said ""hello""");
  WRITELN(quote);
END.
