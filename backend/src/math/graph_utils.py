"""
Graph Utilities — Safe expression evaluation and OCR text extraction.

Contains:
- _safe_evaluate_expression: SymPy-based safe math evaluator (Phase 0 security fix)
- ocr_extract_text: Tesseract OCR for math image extraction

Extracted from main.py L815-L904 (Phase 0 security-fixed version).
"""

import re
import os
import logging
from typing import Optional

logger = logging.getLogger("math_assistant.graph")


def safe_evaluate_expression(expr_str: str, x_array):
    """Safely evaluate a mathematical expression string over a numpy array.

    Uses SymPy's sympify() to parse the expression (rejecting arbitrary Python)
    and lambdify() to convert it to a numpy-callable function. This is safe
    because sympify() only understands mathematical syntax, not arbitrary code.

    Args:
        expr_str: Mathematical expression string (e.g., "sin(x)", "x**2 + 1").
        x_array: numpy array of x values to evaluate the expression over.

    Returns:
        numpy array of y values.

    Raises:
        ValueError: If the expression contains disallowed constructs.
        sympy.SympifyError: If the expression cannot be parsed as math.
    """
    import sympy as sp
    import numpy as np

    # Reject expressions containing dangerous patterns before parsing
    _BLOCKED_PATTERNS = [
        "__", "import", "exec", "eval", "compile", "open", "getattr",
        "setattr", "delattr", "globals", "locals", "vars", "dir",
        "breakpoint", "exit", "quit", "input", "print", "os.",
        "sys.", "subprocess", "shutil", "pathlib",
    ]
    expr_lower = expr_str.lower().replace(" ", "")
    for pattern in _BLOCKED_PATTERNS:
        if pattern in expr_lower:
            raise ValueError(f"Blocked: expression contains disallowed pattern '{pattern}'")

    # Replace caret with power operator
    sanitized = re.sub(r'\^', '**', expr_str.strip())

    # Define allowed SymPy symbols and functions for parsing
    x = sp.Symbol("x")
    _local_dict = {
        "x": x, "e": sp.E, "pi": sp.pi,
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "exp": sp.exp, "log": sp.log, "ln": sp.log,
        "sqrt": sp.sqrt, "abs": sp.Abs,
        "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan,
        "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
        "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
        "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
        "ceiling": sp.ceiling, "floor": sp.floor,
    }

    # Parse through SymPy — rejects arbitrary Python code
    sym_expr = sp.sympify(sanitized, locals=_local_dict)

    # Convert to numpy-callable function — safe, no code execution
    f = sp.lambdify(x, sym_expr, modules=["numpy"])
    y = f(x_array)

    # Ensure result is array (handles constant expressions like "5" or "pi")
    if not hasattr(y, "__len__"):
        y = np.full_like(x_array, float(y))

    return y


def ocr_extract_text(image) -> str:
    """Extract text from an image using Tesseract OCR.

    Args:
        image: PIL Image object.

    Returns:
        Extracted text string, or error message if OCR fails.
    """
    try:
        import pytesseract
        from PIL import ImageEnhance as enhance

        # Set tesseract binary path for common install locations
        for _tess_path in [
            "/opt/homebrew/bin/tesseract",   # macOS Apple Silicon (brew)
            "/usr/local/bin/tesseract",       # macOS Intel (brew)
            "/usr/bin/tesseract",             # Linux
        ]:
            if os.path.exists(_tess_path):
                pytesseract.pytesseract.tesseract_cmd = _tess_path
                break
        gray      = image.convert("L")
        contrast  = enhance.Contrast(gray).enhance(2.0)
        sharpened = enhance.Sharpness(contrast).enhance(2.0)
        text = pytesseract.image_to_string(sharpened, config='--psm 6').strip()
        text = ' '.join(text.replace('\n', ' ').split())
        return text
    except ImportError:
        return "ERROR_NO_PYTESSERACT"
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""
