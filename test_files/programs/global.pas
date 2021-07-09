program global;

var g : integer;

procedure myproc(a : integer);
begin
    g := a * 4;
end;

begin
    myproc(7);
end.
