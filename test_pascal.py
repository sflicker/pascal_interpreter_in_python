import os
from pathlib import Path

from test_program import ProgramTestCase
from test_expression import ExpressionTestCase
from test_statement import StatementTestCase
import unittest

class PasscalTestCase(unittest.TestCase):
    pass

def suite():

        def addExpressionTests(test_suite):
            test_directory = "test_files/expressions"
            for file in os.listdir(test_directory):
                print("testfile", file)
                testfile = os.path.join(test_directory, file)
                testCase = ExpressionTestCase()
                testCase.set_testfile(testfile)
                test_suite.addTest(testCase)

        # TODO convert these to program tests
        # def addStatementTests(test_suite):
        #         test_directory = "test_files/statements"
        #         for file in os.listdir(test_directory):
        #             print("testfile", file)
        #             testfile = os.path.join(test_directory, file)
        #             testCase = StatementTestCase()
        #             testCase.set_testfile(testfile)
        #             test_suite.addTest(testCase)

        def addProgramTests(test_suite):
            test_directory = "test_files/programs"
            for file in os.listdir(test_directory):
                if file.endswith(".pas"):
                    testfile = os.path.join(test_directory, file)
                    p = Path(testfile)

                    #make sure an expect file also exists
                    extensions = "".join(p.suffixes)
                    expectfilename = str(p).replace(extensions, ".exp")
                    if os.path.isfile(expectfilename):
                        print("testfile", file)
                        testCase = ProgramTestCase()
                        testCase.set_testfile(testfile)
                        test_suite.addTest(testCase)

        test_suite = unittest.TestSuite()
        addExpressionTests(test_suite)
        #addStatementTests(test_suite)
        addProgramTests(test_suite)
        return test_suite

mySuite = suite()

runner = unittest.TextTestRunner()
runner.run(mySuite)