"""Security tests for the graph plotter eval() fix (Phase 0).

Validates that:
1. Safe mathematical expressions evaluate correctly via SymPy.
2. Malicious/arbitrary Python code is blocked and cannot execute.
3. All previously supported math functions still work after the fix.

This test file was created as part of Phase 0 security remediation.
The original eval() at main.py L876 has been replaced with
_safe_evaluate_expression() using SymPy sympify + lambdify.
"""

import unittest
import sys
from pathlib import Path

import numpy as np

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import _safe_evaluate_expression


class TestSafeExpressionEvaluator(unittest.TestCase):
    """Verify _safe_evaluate_expression blocks attacks and handles math."""

    def setUp(self):
        """Create a standard x array for all tests."""
        self.x = np.linspace(-10, 10, 100)

    # ─── Safe expressions that MUST work ─────────────────────────────

    def test_polynomial(self):
        """x**2 + 3*x + 1 should evaluate without error."""
        y = _safe_evaluate_expression("x**2 + 3*x + 1", self.x)
        self.assertEqual(len(y), len(self.x))
        # Check a known value: find index closest to x=0
        idx_zero = int(np.argmin(np.abs(self.x)))
        x_val = self.x[idx_zero]
        expected = x_val**2 + 3*x_val + 1
        self.assertAlmostEqual(y[idx_zero], expected, places=5)

    def test_sin(self):
        """sin(x) should return values in [-1, 1]."""
        y = _safe_evaluate_expression("sin(x)", self.x)
        self.assertTrue(np.all(np.abs(y) <= 1.0 + 1e-10))

    def test_cos(self):
        """cos(x) should return values in [-1, 1]."""
        y = _safe_evaluate_expression("cos(x)", self.x)
        self.assertTrue(np.all(np.abs(y) <= 1.0 + 1e-10))

    def test_tan(self):
        """tan(x) should evaluate (may contain large values near pi/2)."""
        x_safe = np.linspace(-1, 1, 50)  # avoid asymptotes
        y = _safe_evaluate_expression("tan(x)", x_safe)
        self.assertEqual(len(y), len(x_safe))

    def test_exp(self):
        """exp(x) should be positive everywhere."""
        x_small = np.linspace(-5, 5, 50)
        y = _safe_evaluate_expression("exp(x)", x_small)
        self.assertTrue(np.all(y > 0))

    def test_log(self):
        """log(x) should work for positive x values."""
        x_pos = np.linspace(0.1, 10, 50)
        y = _safe_evaluate_expression("log(x)", x_pos)
        self.assertEqual(len(y), len(x_pos))

    def test_sqrt(self):
        """sqrt(x) should work for non-negative x values."""
        x_pos = np.linspace(0, 10, 50)
        y = _safe_evaluate_expression("sqrt(x)", x_pos)
        self.assertTrue(np.all(y >= 0))

    def test_abs(self):
        """abs(x) should return non-negative values."""
        y = _safe_evaluate_expression("abs(x)", self.x)
        self.assertTrue(np.all(y >= 0))

    def test_caret_to_power(self):
        """x^2 (caret notation) should be treated as x**2."""
        y = _safe_evaluate_expression("x^2", self.x)
        expected = self.x ** 2
        np.testing.assert_array_almost_equal(y, expected)

    def test_constant_expression(self):
        """A constant like '5' should return an array of 5s."""
        y = _safe_evaluate_expression("5", self.x)
        self.assertEqual(len(y), len(self.x))
        np.testing.assert_array_almost_equal(y, np.full_like(self.x, 5.0))

    def test_pi_constant(self):
        """pi should evaluate to approximately 3.14159."""
        y = _safe_evaluate_expression("pi", self.x)
        self.assertAlmostEqual(y[0], np.pi, places=4)

    def test_composite_expression(self):
        """sin(x) + cos(x) should evaluate correctly."""
        y = _safe_evaluate_expression("sin(x) + cos(x)", self.x)
        expected = np.sin(self.x) + np.cos(self.x)
        np.testing.assert_array_almost_equal(y, expected, decimal=5)

    def test_arcsin(self):
        """arcsin(x) should work for x in [-1, 1]."""
        x_safe = np.linspace(-0.99, 0.99, 50)
        y = _safe_evaluate_expression("arcsin(x)", x_safe)
        self.assertEqual(len(y), len(x_safe))

    def test_sinh(self):
        """sinh(x) should evaluate without error."""
        y = _safe_evaluate_expression("sinh(x)", self.x)
        self.assertEqual(len(y), len(self.x))

    def test_cosh(self):
        """cosh(x) should always be >= 1."""
        y = _safe_evaluate_expression("cosh(x)", self.x)
        self.assertTrue(np.all(y >= 1.0 - 1e-10))

    def test_tanh(self):
        """tanh(x) should return values in [-1, 1]."""
        y = _safe_evaluate_expression("tanh(x)", self.x)
        self.assertTrue(np.all(np.abs(y) <= 1.0 + 1e-10))

    # ─── Malicious expressions that MUST be BLOCKED ──────────────────

    def test_blocks_os_import(self):
        """Attempt to import os module must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("__import__('os').system('ls')", self.x)

    def test_blocks_sys_access(self):
        """Attempt to access sys module must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("sys.exit(1)", self.x)

    def test_blocks_open_file(self):
        """Attempt to open a file must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("open('/etc/passwd')", self.x)

    def test_blocks_exec(self):
        """Attempt to use exec() must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("exec('print(1)')", self.x)

    def test_blocks_eval(self):
        """Attempt to use eval() inside expression must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("eval('1+1')", self.x)

    def test_blocks_dunder(self):
        """Attempt to access __builtins__ must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("__builtins__", self.x)

    def test_blocks_subprocess(self):
        """Attempt to use subprocess must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("subprocess.call(['ls'])", self.x)

    def test_blocks_getattr(self):
        """Attempt to use getattr must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("getattr(x, '__class__')", self.x)

    def test_blocks_compile(self):
        """Attempt to use compile() must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("compile('1', '', 'exec')", self.x)

    def test_blocks_globals(self):
        """Attempt to access globals() must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("globals()", self.x)

    def test_blocks_pathlib(self):
        """Attempt to use pathlib must raise an error."""
        with self.assertRaises(Exception):
            _safe_evaluate_expression("pathlib.Path('.')", self.x)


if __name__ == "__main__":
    unittest.main()
