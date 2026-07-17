from mcp.server.fastmcp import FastMCP
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

# Initialize FastMCP server
mcp = FastMCP("SymPy Math Server")

@mcp.tool()
def differentiate(expression: str, variable: str = 'x') -> dict:
    """Calculate the derivative of a mathematical expression.
    
    Args:
        expression: The mathematical expression (e.g. 'x**2 + 2*x')
        variable: The variable to differentiate with respect to (default 'x')
    """
    try:
        var = sp.Symbol(variable)
        expr = parse_expr(expression)
        result = sp.diff(expr, var)
        return {
            "result": str(result),
            "latex": sp.latex(result)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def integrate(expression: str, variable: str = 'x') -> dict:
    """Calculate the indefinite integral of a mathematical expression.
    
    Args:
        expression: The mathematical expression
        variable: The integration variable (default 'x')
    """
    try:
        var = sp.Symbol(variable)
        expr = parse_expr(expression)
        result = sp.integrate(expr, var)
        return {
            "result": str(result),
            "latex": sp.latex(result)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def simplify(expression: str) -> dict:
    """Simplify a mathematical expression.
    
    Args:
        expression: The mathematical expression
    """
    try:
        expr = parse_expr(expression)
        result = sp.simplify(expr)
        return {
            "result": str(result),
            "latex": sp.latex(result)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def solve(equation: str, variable: str = 'x') -> dict:
    """Solve an algebraic equation. Note: write the expression such that it equals 0. 
    E.g. for x^2 = 4, write x**2 - 4.
    
    Args:
        equation: The equation expression equal to 0
        variable: The variable to solve for (default 'x')
    """
    try:
        var = sp.Symbol(variable)
        expr = parse_expr(equation)
        result = sp.solve(expr, var)
        return {
            "result": str(result),
            "latex": sp.latex(result)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport='stdio')
