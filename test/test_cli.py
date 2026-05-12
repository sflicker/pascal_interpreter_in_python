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
        self.assertEqual(result.stdout, "")
        self.assertIn("ParserError:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_debug_step_enters_procedure_context(self):
        result = self.run_cli(
            "--debug",
            "test/test_files/programs/alpha.pas",
            input_text="s\ns\nwhere\nq\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Paused at PROGRAM MAIN, line 11", result.stderr)
        self.assertIn("Paused at PROCEDURE ALPHA, line 6", result.stderr)
        self.assertIn("Paused at PROCEDURE ALPHA, line 7", result.stderr)
        self.assertIn("=>   7    writeln(x);", result.stderr)

    def test_debug_next_steps_over_procedure_call(self):
        result = self.run_cli(
            "--debug",
            "test/test_files/programs/alpha.pas",
            input_text="n\n\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "30\n")
        self.assertIn("Paused at PROGRAM MAIN, line 11", result.stderr)
        self.assertNotIn("Paused at PROCEDURE ALPHA", result.stderr)
        self.assertIn("Program finished.", result.stderr)

    def test_debug_next_stays_in_current_procedure_frame(self):
        result = self.run_cli(
            "--debug",
            "test/test_files/programs/alpha.pas",
            input_text="s\nn\nq\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Paused at PROCEDURE ALPHA, line 6", result.stderr)
        self.assertIn("Paused at PROCEDURE ALPHA, line 7", result.stderr)

    def test_debug_breakpoint_locals_print_and_continue(self):
        result = self.run_cli(
            "--debug",
            "test/test_files/programs/alpha.pas",
            input_text="b 6\nc\nlocals\np A\nstack\nc\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "30\n")
        self.assertIn("Breakpoint set at line 6", result.stderr)
        self.assertIn("Paused at PROCEDURE ALPHA, line 6", result.stderr)
        self.assertIn("A = 8", result.stderr)
        self.assertIn("B = 7", result.stderr)
        self.assertIn("X = None", result.stderr)
        self.assertIn("#0 PROCEDURE ALPHA", result.stderr)
        self.assertIn("#1 PROGRAM MAIN", result.stderr)

    def test_debug_prompts_when_program_finishes(self):
        result = self.run_cli(
            "--debug",
            "test/test_files/programs/writelntest.pas",
            input_text="c\n\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "25\n")
        self.assertIn("Program finished.", result.stderr)
        self.assertIn("Press Enter to exit the debugger.", result.stderr)

    def test_debug_parser_failure_does_not_enter_debugger(self):
        result = self.run_cli("--debug", "test/test_files/programs/syntax_unknown_type.pas")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("ParserError:", result.stderr)
        self.assertNotIn("Paused at", result.stderr)
        self.assertNotIn("debug>", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_lexer_failure_does_not_print_traceback(self):
        result = self.run_cli("test/test_files/programs/syntax_unclosed_string.pas")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("LexerError:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
