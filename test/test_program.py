import unittest
import json
import io
import os
import sys
import tempfile
from pathlib import Path

from pascal_interpreter.pascal_tester import run_program


def is_verbose():
    return os.environ.get("PASCAL_TEST_VERBOSE") == "1"


class ProgramTestCase(unittest.TestCase):

    def set_testfile(self, testfile):
        self.testfile = testfile

    def __str__(self):
        return getattr(self, "testfile", super().__str__())

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
            expectexitcode = expect["exitcode"]
            stdin = expect.get("input")
            files = expect.get("files")
            expected_files = expect.get("expected_files", {})
            source_dir = expect.get("source_dir")

            verbose = is_verbose()
            original_stdin = sys.stdin
            original_cwd = os.getcwd()
            tempdir = None
            try:
                if stdin is not None:
                    sys.stdin = io.StringIO(stdin)
                if files is not None or source_dir is not None:
                    tempdir = tempfile.TemporaryDirectory()
                    os.chdir(tempdir.name)
                if files is not None:
                    for name, contents in files.items():
                        file_path = Path(name)
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(contents)
                source_name = None
                if source_dir is not None:
                    source_path = Path(source_dir) / p.name
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                    source_path.write_text(prog)
                    source_name = str(source_path)
                (memory, output, exitcode) = run_program(prog, trace_tokens=verbose, verbose=verbose, source_name=source_name)
                actual_files = {}
                for name in expected_files:
                    actual_files[name] = Path(name).read_text()
            finally:
                sys.stdin = original_stdin
                os.chdir(original_cwd)
                if tempdir is not None:
                    tempdir.cleanup()

            if expected_files:
                try:
                    assert actual_files == expected_files, f"Files {actual_files} do not match {expected_files} for {self.testfile}"
                except UnboundLocalError:
                    raise AssertionError(f"Expected files were not checked for {self.testfile}")

            assert memory == expectmemory, f"Memory {memory} does not match {expectmemory} for {self.testfile}"
            assert output == expectoutput, f"Output {output} does not match {expectoutput} for {self.testfile}"
            assert exitcode == expectexitcode, f"exitcode {exitcode} does not match {expectexitcode} for {self.testfile}"
            if verbose:
                print(self.testfile, "Passed")
