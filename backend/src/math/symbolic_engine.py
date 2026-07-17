"""
Symbolic Mathematics Engine — SymPy-based exact computation.

Extracted from main.py L585-L643. Provides differentiation, integration,
equation solving, simplification, and matrix operations using SymPy.
All methods are stateless (static) and safe for concurrent use.
"""

import re
import ast
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("math_assistant.symbolic")


class SymbolicMathEngine:
    """SymPy-powered symbolic math solver for exact computation."""

    @staticmethod
    def differentiate(expression: str, variable: str = "x") -> Optional[str]:
        """Compute the derivative of an expression with respect to a variable."""
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            expr = sp.sympify(re.sub(r'\^', '**', expression.strip()))
            return f"d/d{variable}[{expression}] = {sp.simplify(sp.diff(expr, var))}"
        except Exception:
            return None

    @staticmethod
    def integrate(expression: str, variable: str = "x") -> Optional[str]:
        """Compute the indefinite integral of an expression."""
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            expr = sp.sympify(re.sub(r'\^', '**', expression.strip()))
            return f"integral({expression}) d{variable} = {sp.integrate(expr, var)} + C"
        except Exception:
            return None

    @staticmethod
    def solve_equation(equation: str, variable: str = "x") -> Optional[str]:
        """Solve an equation for a given variable."""
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            eq_str = re.sub(r'\^', '**', equation.strip())
            if "=" in eq_str:
                lhs, rhs = eq_str.split("=", 1)
                eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            else:
                eq = sp.sympify(eq_str)
            return f"Solutions for {variable}: {sp.solve(eq, var)}"
        except Exception:
            return None

    @staticmethod
    def try_solve(expression: str) -> Optional[str]:
        """Attempt to simplify or solve a general expression."""
        try:
            import sympy as sp
            x, y, z, t = sp.symbols('x y z t')
            expr_str = re.sub(r'\^', '**', expression.strip())
            result = sp.simplify(sp.sympify(expr_str, locals={
                'x': x, 'y': y, 'z': z, 't': t,
                'sin': sp.sin, 'cos': sp.cos, 'exp': sp.exp,
                'log': sp.log, 'sqrt': sp.sqrt, 'pi': sp.pi}))
            return str(result)
        except Exception:
            return None

    @staticmethod
    def matrix_operations(matrix_str: str) -> Optional[Dict[str, Any]]:
        """Compute determinant, rank, eigenvalues, and trace of a matrix."""
        try:
            import sympy as sp
            M = sp.Matrix(ast.literal_eval(matrix_str))
            return {
                "determinant": str(M.det()),
                "rank": M.rank(),
                "eigenvalues": str(M.eigenvals()),
                "trace": str(M.trace()),
            }
        except Exception:
            return None
