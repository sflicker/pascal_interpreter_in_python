program PointerAssignmentTypeError;

type
  IntPtr = ^INTEGER;
  CharPtr = ^CHAR;

var
  p: IntPtr;
  q: CharPtr;

begin
  p := q;
end.
