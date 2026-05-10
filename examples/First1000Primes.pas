program First1000Primes;

var
  count, candidate, divisor, isprime : Integer;

begin
  count := 0;
  candidate := 2;

  while count < 1000 do
  begin
    isprime := 1;
    divisor := 2;

    while (divisor * divisor <= candidate) and (isprime = 1) do
    begin
      if candidate mod divisor = 0 then
        isprime := 0
      else
        divisor := divisor + 1;
    end;

    if isprime = 1 then
    begin
      writeln(candidate);
      count := count + 1;
    end;

    candidate := candidate + 1;
  end;
end.
