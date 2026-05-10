program builtin_ord_chr_pred_succ;

var
  code, priorNumber, nextNumber : Integer;
  ch, priorChar, nextChar : Char;

begin
  code := ord('A');
  ch := chr(66);
  priorNumber := pred(10);
  nextNumber := succ(10);
  priorChar := pred('B');
  nextChar := succ('B');

  writeln(code);
  writeln(ch);
  writeln(priorNumber);
  writeln(nextNumber);
  writeln(priorChar);
  writeln(nextChar);
end.
