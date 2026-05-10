from pascal_interpreter.pascal_tester import run_expression, run_statement
import unittest
import json
import os


def is_verbose():
    return os.environ.get("PASCAL_TEST_VERBOSE") == "1"

class StatementTestCase(unittest.TestCase):

    def set_testfile(self, testfile):
        self.testfile = testfile

    def __str__(self):
        return getattr(self, "testfile", super().__str__())

    def runTest(self):
        if hasattr(self, 'testfile'):
            textfile = open(self.testfile, 'r')
            text = textfile.read()
            test = json.JSONDecoder().decode(text)
            textfile.close()
            statement = test["statement"]
            if isinstance(statement, list):
                statement = "\n".join(statement)
            verbose = is_verbose()
            assert run_statement(statement, trace_tokens=verbose, verbose=verbose) == test["expected"]
