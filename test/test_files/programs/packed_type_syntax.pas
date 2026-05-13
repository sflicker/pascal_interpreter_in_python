program PackedTypeSyntax;

type
  PackedNumbers = PACKED ARRAY [1..3] OF INTEGER;
  PackedLetters = PACKED SET OF CHAR;
  PackedPoint = PACKED RECORD
    x, y: INTEGER;
  END;

var
  numbers: PackedNumbers;
  letters: PackedLetters;
  point: PackedPoint;

begin
  numbers[1] := 4;
  letters := ['a'..'c'];
  point.x := numbers[1];
  point.y := 6;
  WRITELN(point.x + point.y);
  WRITELN('b' IN letters);
end.
