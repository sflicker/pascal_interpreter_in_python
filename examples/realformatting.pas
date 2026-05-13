{ This exercise is [Section 1.9 exer. 3]  from Problem solving and structured programming in pascal by Hoffman }

program RealFormatting (INPUT, OUTPUT);

var x : real;

begin
   x := -15.564;
   WRITELN(x :8:4, x :8:3, x :8:2, x :8:1, x :8:0, x :8);
end.
