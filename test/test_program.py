import unittest
import json
import io
import os
import sys
from pathlib import Path

from pascal_interpreter.pascal_tester import run_program


def is_verbose():
    return os.environ.get("PASCAL_TEST_VERBOSE") == "1"


class ProgramTestCase(unittest.TestCase):

    def set_testfile(self, testfile):
        self.testfile = testfile

    def __str__(self):
        return getattr(self, "testfile", super().__str__())

    def runTest(self):
        if hasattr(self, 'testfile'):
            progfile = open(self.testfile, 'r')
            prog = progfile.read()
            progfile.close()

            p = Path(self.testfile)
            extensions = "".join(p.suffixes)
            expectfilename = str(p).replace(extensions, ".exp")
            expectfile = open(expectfilename, 'r')
            expect = json.JSONDecoder().decode(expectfile.read())
            expectfile.close()
            expectoutput = expect["output"]
            expectmemory = expect["memory"]
            expectexitcode = expect["exitcode"]
            stdin = expect.get("input")

            verbose = is_verbose()
            if stdin is None:
                (memory, output, exitcode) = run_program(prog, trace_tokens=verbose, verbose=verbose)
            else:
                original_stdin = sys.stdin
                try:
                    sys.stdin = io.StringIO(stdin)
                    (memory, output, exitcode) = run_program(prog, trace_tokens=verbose, verbose=verbose)
                finally:
                    sys.stdin = original_stdin

            assert memory == expectmemory, f"Memory {memory} does not match {expectmemory} for {self.testfile}"
            assert output == expectoutput, f"Output {output} does not match {expectoutput} for {self.testfile}"
            assert exitcode == expectexitcode, f"exitcode {exitcode} does not match {expectexitcode} for {self.testfile}"
            if verbose:
                print(self.testfile, "Passed")
