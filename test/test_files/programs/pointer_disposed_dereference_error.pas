program PointerDisposedDereferenceError;

type
  IntPtr = ^INTEGER;

var
  p, q: IntPtr;

begin
  NEW(p);
  p^ := 7;
  q := p;
  DISPOSE(p);
  writeln(q^);
end.
