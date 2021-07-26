import json
import unittest
from pascal_main import run_expression

class ExpressionTestCase(unittest.TestCase):

    def set_testfile(self, testfile):
        self.testfile = testfile

    def __str__(self):
        return self.testfile

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
            actual = run_expression(expression)
            assert run_expression(expression) == expected, f"{actual} does not match {expected} for {self.testfile}"
            print(self.testfile, "Passed")