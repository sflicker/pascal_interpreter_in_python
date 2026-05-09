#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT_DIR}/src:${ROOT_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

cd "${ROOT_DIR}"

python3 - <<'PY'
import unittest
from pathlib import Path

from test.test_expression import ExpressionTestCase
from test.test_program import ProgramTestCase
from test.test_statement import StatementTestCase


ROOT = Path.cwd()
TEST_FILES_DIR = ROOT / "test" / "test_files"


def add_expression_tests(test_suite):
    test_directory = TEST_FILES_DIR / "expressions"
    for testfile in sorted(test_directory.iterdir()):
        if testfile.suffix == ".expr":
            test_case = ExpressionTestCase()
            test_case.set_testfile(str(testfile))
            test_suite.addTest(test_case)


def add_statement_tests(test_suite):
    test_directory = TEST_FILES_DIR / "statements"
    for testfile in sorted(test_directory.iterdir()):
        if testfile.suffix == ".stat":
            test_case = StatementTestCase()
            test_case.set_testfile(str(testfile))
            test_suite.addTest(test_case)


def add_program_tests(test_suite):
    test_directory = TEST_FILES_DIR / "programs"
    for testfile in sorted(test_directory.iterdir()):
        if testfile.suffix != ".pas":
            continue

        expectfile = testfile.with_suffix(".exp")
        if expectfile.is_file():
            test_case = ProgramTestCase()
            test_case.set_testfile(str(testfile))
            test_suite.addTest(test_case)


suite = unittest.TestSuite()
add_expression_tests(suite)
add_statement_tests(suite)
add_program_tests(suite)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if not result.wasSuccessful():
    raise SystemExit(1)
PY
