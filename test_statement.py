from pascal_main import run_expression, run_statement
import unittest
import json

class StatementTestCase(unittest.TestCase):

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
            statement = test["statement"]
            if isinstance(statement, list):
                statement = "\n".join(statement)
            assert run_statement(statement) == test["expected"]
