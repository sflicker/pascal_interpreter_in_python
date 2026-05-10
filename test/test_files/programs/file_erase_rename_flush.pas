PROGRAM FileEraseRenameFlush;
VAR
  f, old_file: TEXT;
BEGIN
  ASSIGN(f, 'new.txt');
  REWRITE(f);
  WRITE(f, 'ready');
  FLUSH(f);
  CLOSE(f);
  RENAME(f, 'renamed.txt');

  ASSIGN(old_file, 'old.txt');
  ERASE(old_file);
END.
