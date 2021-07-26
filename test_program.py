import unittest
import json
from pathlib import Path

from pascal_main import run_program


class ProgramTestCase(unittest.TestCase):

    def set_testfile(self, testfile):
        self.testfile = testfile

    def __str__(self):
        return self.testfile

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

            (memory, output, exitcode) = run_program(prog)

            assert memory == expectmemory, f"Memory {memory} does not match {expectmemory} for {self.testfile}"
            assert output == expectoutput, f"Output {output} does not match {expectoutput} for {self.testfile}"
            assert exitcode == expectexitcode, f"exitcode {exitcode} does not match {expectexitcode} for {self.testfile}"
            print(self.testfile, "Passed")

