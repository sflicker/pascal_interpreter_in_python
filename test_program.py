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

            (memory, output) = run_program(prog)

            assert memory == expectmemory
            assert output == expectoutput

