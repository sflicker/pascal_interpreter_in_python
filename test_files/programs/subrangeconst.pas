program subrangeconst;
{ this program is not legal. Should return an error code }
const Range = 1..10;

var A : array[Range] of Integer;

begin
  A[1] := 1;
  writeln(A[1]);
end.