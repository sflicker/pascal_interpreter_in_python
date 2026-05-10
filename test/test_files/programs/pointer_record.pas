PROGRAM PointerRecord;
TYPE
  NodePtr = ^Node;
  Node = RECORD
    value: INTEGER;
    next: NodePtr;
  END;
VAR
  p, q: NodePtr;
BEGIN
  p := NIL;
  WRITELN(p = NIL);

  NEW(p);
  p^.value := 10;
  p^.next := NIL;

  NEW(q);
  q^.value := 20;
  q^.next := p;

  WRITELN(q^.value + q^.next^.value);
  DISPOSE(q);
  DISPOSE(p);
  WRITELN(p = NIL);
END.
