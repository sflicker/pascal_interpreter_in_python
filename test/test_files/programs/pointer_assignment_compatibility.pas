program PointerAssignmentCompatibility;

type
  IntPtr = ^INTEGER;

var
  p, q: IntPtr;

begin
  NEW(p);
  p^ := 42;
  q := p;
  writeln(q^);
  q := NIL;
  writeln(q = NIL);
  DISPOSE(p);
end.
