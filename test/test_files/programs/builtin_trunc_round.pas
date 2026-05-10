program builtin_trunc_round;

var
  truncPositive, truncNegative : Integer;
  roundPositive, roundNegative : Integer;
  roundInteger : Integer;

begin
  truncPositive := trunc(3.7);
  truncNegative := trunc(-3.7);
  roundPositive := round(3.7);
  roundNegative := round(-3.7);
  roundInteger := round(5);

  writeln(truncPositive);
  writeln(truncNegative);
  writeln(roundPositive);
  writeln(roundNegative);
  writeln(roundInteger);
end.
