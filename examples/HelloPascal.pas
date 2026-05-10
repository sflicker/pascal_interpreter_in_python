{ From "Program Solving & Structured Programming in Pascal" by Koffman}
program HelloPascal(INPUT, OUTPUT);
var
    LETTER1, LETTER2, LETTER3 : CHAR;

begin 
    WRITELN('Enter a 3 letter nickname and press return.');
    READLN(LETTER1, LETTER2, LETTER3);
    WRITELN('Hello ', LETTER1, LETTER2, LETTER3, '.');
    WRITELN('We hope you enjoy studying pascal!');
end.
