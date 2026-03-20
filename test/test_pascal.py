from pathlib import Path

from test.test_program import ProgramTestCase
from test.test_expression import ExpressionTestCase
from test.test_statement import StatementTestCase
import unittest


TEST_FILES_DIR = Path(__file__).resolve().parent / "test_files"

class PasscalTestCase(unittest.TestCase):
    pass

def suite():

        def addExpressionTests(test_suite):
            test_directory = TEST_FILES_DIR / "expressions"
            for testfile in test_directory.iterdir():
                print("testfile", testfile.name)
                testCase = ExpressionTestCase()
                testCase.set_testfile(str(testfile))
                test_suite.addTest(testCase)

        # TODO convert these to program tests
        # def addStatementTests(test_suite):
        #         test_directory = "test/test_files/statements"
        #         for file in os.listdir(test_directory):
        #             print("testfile", file)
        #             testfile = os.path.join(test_directory, file)
        #             testCase = StatementTestCase()
        #             testCase.set_testfile(testfile)
        #             test_suite.addTest(testCase)

        def addProgramTests(test_suite):
            test_directory = TEST_FILES_DIR / "programs"
            for testfile in test_directory.iterdir():
                if testfile.suffix == ".pas":
                    p = Path(testfile)

                    #make sure an expect file also exists
                    extensions = "".join(p.suffixes)
                    expectfilename = str(p).replace(extensions, ".exp")
                    if Path(expectfilename).is_file():
                        print("testfile", testfile.name)
                        testCase = ProgramTestCase()
                        testCase.set_testfile(str(testfile))
                        test_suite.addTest(testCase)

        test_suite = unittest.TestSuite()
        addExpressionTests(test_suite)
        #addStatementTests(test_suite)
        addProgramTests(test_suite)
        return test_suite

mySuite = suite()

runner = unittest.TextTestRunner()
runner.run(mySuite)
