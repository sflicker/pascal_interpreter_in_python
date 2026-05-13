{ This exercise is [Section 1.9 exer. 2]  from Problem solving and structured programming in pascal by Hoffman }

program COUNTCOINS(INPUT, OUTPUT);

var NICKLES, PENNIES, DIMES, QUARTERS, COINS, CENTS : INTEGER;

begin
    write('How many quarters do you have? '); READLN(QUARTERS);
    write('How many dimes do you have? '); READLN(DIMES);
    write('How many nickles do you have? '); READLN(NICKLES);
    write('How many pennies do you have? '); READLN(PENNIES);
    COINS := QUARTERS + DIMES + NICKLES + PENNIES;
    CENTS := 25*QUARTERS + 10*DIMES + 5*NICKLES + PENNIES;
    WRITELN('You have ' , COINS:2, ' coins.');
    WRITELN('Their value is ', CENTS :3, ' cents.');
end.