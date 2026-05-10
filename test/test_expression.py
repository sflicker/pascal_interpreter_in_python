import json
import os
import unittest
from pascal_interpreter.pascal_tester import run_expression


def is_verbose():
    return os.environ.get("PASCAL_TEST_VERBOSE") == "1"

class ExpressionTestCase(unittest.TestCase):

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
            expression = test["expr"]
            expected = test["result"]
            if isinstance(expression, list):
                expression = "\n".join(expression)
            verbose = is_verbose()
            actual = run_expression(expression, trace_tokens=verbose, verbose=verbose)
            assert actual == expected, f"{actual} does not match {expected} for {self.testfile}"
            if verbose:
                print(self.testfile, "Passed")
