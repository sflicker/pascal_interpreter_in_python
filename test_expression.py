import json
import unittest
from pascal_main import run_expression

class ExpressionTestCase(unittest.TestCase):

    def set_testfile(self, testfile):
        self.testfile = testfile

    def __str__(self):
        return self.testfile

    def runTest(self):
        textfile = open(self.testfile, 'r')
        text = textfile.read()
        test = json.JSONDecoder().decode(text)
        textfile.close()
        expression = test["expr"]
        expected = test["result"]
        if isinstance(expression, list):
            expression = "\n".join(expression)
        assert run_expression(expression) == expected