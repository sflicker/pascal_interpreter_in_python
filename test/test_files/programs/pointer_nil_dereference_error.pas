program PointerNilDereferenceError;

type
  IntPtr = ^INTEGER;

var
  p: IntPtr;

begin
  p := NIL;
  writeln(p^);
end.
