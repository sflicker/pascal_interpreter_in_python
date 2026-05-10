program input_retry(input, output);

var number : Integer;
begin
  writeln('Please enter an integer between 0 and 10');
  readln(number);
  while (number < 0) or (number > 10) do
  begin
    writeln('Try again please, integer between 0 and 10');
    read(number);
  end;
  writeln(number);
end.
