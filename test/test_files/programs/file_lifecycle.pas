PROGRAM FileLifecycle;
VAR
  source, target: TEXT;
BEGIN
  ASSIGN(source, 'source.txt');
  RESET(source);
  CLOSE(source);

  ASSIGN(target, 'target.txt');
  REWRITE(target);
  CLOSE(target);
END.
