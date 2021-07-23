program global;

var g : integer;

procedure myproc(a : integer);
begin
    g := a * 4 + 1;
    writeln(g);
end;

begin
    g := 1;
    writeln(g);
    myproc(7);
    writeln(g);
end.
