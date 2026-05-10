import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CLITestCase(unittest.TestCase):

    def run_cli(self, *args, input_text=None):
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
        return subprocess.run(
            [str(ROOT / "run_pascal.sh"), *args],
            cwd=ROOT,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def test_default_output_is_quiet(self):
        result = self.run_cli("test/test_files/programs/writelntest.pas")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "25\n")
        self.assertEqual(result.stderr, "")

    def test_trace_tokens_goes_to_stderr(self):
        result = self.run_cli("--trace-tokens", "test/test_files/programs/writelntest.pas")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "25\n")
        self.assertIn("tokens", result.stderr)
        self.assertIn("Token(TokenType.PROGRAM", result.stderr)

    def test_parser_failure_returns_nonzero(self):
        result = self.run_cli("test/test_files/programs/nestedscopes03.pas")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "100")
        self.assertEqual(result.stderr, "")
