"""Tests for SymbolicMathEngine — extracted from main.py L2634-L2656.

Validates core symbolic math operations: differentiation, integration,
equation solving, and expression simplification via SymPy.
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.src.math.symbolic_engine import SymbolicMathEngine


class TestSymbolicEngine(unittest.TestCase):
    """Verify SymPy-based symbolic computation produces correct results."""

    def setUp(self):
        self.sym = SymbolicMathEngine()

    def test_differentiate(self):
        """d/dx(x^3) should yield 3*x**2."""
        result = self.sym.differentiate("x**3")
        self.assertIsNotNone(result)
        self.assertIn("3*x**2", result.replace(" ", ""))

    def test_integrate(self):
        """integral(x^2) dx should yield x**3/3."""
        result = self.sym.integrate("x**2")
        self.assertIsNotNone(result)
        self.assertIn("x**3", result)

    def test_solve(self):
        """x^2 - 4 = 0 should yield solutions containing 2."""
        result = self.sym.solve_equation("x**2 - 4 = 0")
        self.assertIsNotNone(result)
        self.assertIn("2", result)

    def test_simplify(self):
        """(x^2 - 1)/(x - 1) should simplify to x + 1."""
        result = self.sym.try_solve("(x**2 - 1)/(x - 1)")
        self.assertIsNotNone(result)
        self.assertIn("x + 1", result)


if __name__ == "__main__":
    unittest.main()
