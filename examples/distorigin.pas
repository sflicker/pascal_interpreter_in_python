{ from "Program Solving & Structured Programming in Pascal" by Koffman }
program DISTORIGIN (INPUT, OUTPUT);
{finds the distance from a point to the origin. }
type 
    POINT = record
      XCOORD, YCOORD : REAL
    end;  {POINT}

var
    POINT1: POINT;
    DISTANCE : REAL;

begin
    with point1 do
      begin
        write('X: '); READLN(XCOORD);
        write('Y: '); READLN(YCOORD);
        DISTANCE := SQRT(SQR(XCOORD) + SQR(YCOORD));
        WRITELN('Distance to origin is ', DISTANCE);
      end
end.
