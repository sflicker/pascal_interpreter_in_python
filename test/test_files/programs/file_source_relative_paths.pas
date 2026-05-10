PROGRAM FileSourceRelativePaths;
VAR
  input_file, output_file: TEXT;
  value: INTEGER;
BEGIN
  ASSIGN(input_file, 'input.txt');
  RESET(input_file);
  READLN(input_file, value);
  CLOSE(input_file);

  ASSIGN(output_file, 'nested/output.txt');
  REWRITE(output_file);
  WRITELN(output_file, value + 1);
  CLOSE(output_file);

  WRITELN(value);
END.
