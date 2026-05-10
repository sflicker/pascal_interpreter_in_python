#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT_DIR}/src:${ROOT_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

VERBOSE=0
if [[ "${1:-}" == "--verbose" ]]; then
    VERBOSE=1
    export PASCAL_TEST_VERBOSE=1
    shift
fi

if [[ $# -ne 0 ]]; then
    echo "Usage: $0 [--verbose]" >&2
    exit 2
fi

cd "${ROOT_DIR}"

python3 - "${VERBOSE}" <<'PY'
import sys
import unittest
from pathlib import Path

from test.test_expression import ExpressionTestCase
from test.test_program import ProgramTestCase
from test.test_statement import StatementTestCase
from test.test_cli import CLITestCase


ROOT = Path.cwd()
TEST_FILES_DIR = ROOT / "test" / "test_files"
TEST_GROUPS = (
    ("Expressions", ExpressionTestCase),
    ("Statements", StatementTestCase),
    ("Programs", ProgramTestCase),
    ("CLI", CLITestCase),
)


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


def add_cli_tests(test_suite):
    test_suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(CLITestCase))


def iter_tests(test_suite):
    for test in test_suite:
        if isinstance(test, unittest.TestSuite):
            yield from iter_tests(test)
        else:
            yield test


suite = unittest.TestSuite()
add_expression_tests(suite)
add_statement_tests(suite)
add_program_tests(suite)
add_cli_tests(suite)

totals = {test_class: 0 for _, test_class in TEST_GROUPS}
for test in iter_tests(suite):
    totals[type(test)] += 1

verbose = sys.argv[1] == "1"
runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
result = runner.run(suite)

def test_key(test):
    return getattr(test, "testfile", test.id())


failed_test_keys = {
    test_key(test)
    for test, _ in (
        result.failures
        + result.errors
        + result.unexpectedSuccesses
    )
}

print()
print("Test summary:")
combined_total = 0
combined_failed = 0
for label, test_class in TEST_GROUPS:
    total = totals[test_class]
    failed = sum(
        1
        for test in iter_tests(suite)
        if isinstance(test, test_class) and test_key(test) in failed_test_keys
    )
    passed = total - failed
    combined_total += total
    combined_failed += failed
    print(f"  {label}: {passed} passed, {failed} failed, {total} total")

combined_passed = combined_total - combined_failed
print(f"  Combined: {combined_passed} passed, {combined_failed} failed, {combined_total} total")

if not result.wasSuccessful():
    raise SystemExit(1)
PY
