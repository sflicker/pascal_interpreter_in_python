program SetInComponentTypeError;

var
  letters: SET OF CHAR;

begin
  letters := ['a', 'b'];
  writeln(1 IN letters);
end.
