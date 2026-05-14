program TypedFileTypeError;

var
  values: FILE OF INTEGER;

begin
  ASSIGN(values, 'numbers.dat');
  REWRITE(values);
  WRITE(values, 'bad');
end.
