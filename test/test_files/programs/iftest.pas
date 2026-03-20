program iftest;
 var a, b, c : integer;
BEGIN
  a := 5;
  if a > 4 then
     b := 1
  else
     b := 2;

  if a < 3 then
     c := 1
  else
     c := 2;

  writeln(a);
  writeln(b);
  writeln(c);
END.

