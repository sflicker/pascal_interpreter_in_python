PROGRAM Part12;
VAR
    a, b, c : INTEGER;

PROCEDURE P1;
VAR
    a : REAL;
    k : INTEGER;

    PROCEDURE P2;
    VAR
        a, z : INTEGER;
    BEGIN {P2}
        z := 777;
    END ; {P2}

BEGIN {P1}

END; {P1}

BEGIN {Part12}
    a := 10;
    b := -a;
    c := +b;

END. {Part12}