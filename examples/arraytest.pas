program arraytest (INPUT,OUTPUT);

type
    REALARRAY = array [1..8] of REAL;

var 
   X : REALARRAY;
   AVERAGE : REAL;
   SUM : REAL;
   i : integer;

begin
  X[1] := 10.0;
  X[2] := 13.5;
  X[3] := 5.3;
  X[4] := 693.8;
  X[5] := 92.993;
  X[6] := -39.8;
  X[7] := 0.0;
  X[8] := 393.9;

  SUM := 0.0;

  for i := 1 to 8 do
  begin
     writeln('X[',i,'] - ', X[i] :8:4);
     sum := sum + X[i];
  end;

  writeln('sum: ', sum :8:4);
  
  average := sum/8.0;
  writeln('average: ', average :8:4);
end.



