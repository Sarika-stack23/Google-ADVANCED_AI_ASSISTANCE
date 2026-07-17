from mcp.server.fastmcp import FastMCP
import matplotlib.pyplot as plt
import numpy as np
import io

mcp = FastMCP("Graph Plotter Server")

@mcp.tool()
def plot_function(function_str: str, x_min: float = -10, x_max: float = 10) -> str:
    """Plot a mathematical function and return it as an SVG string.
    
    Args:
        function_str: A python-evaluable math string in terms of x (e.g. 'np.sin(x)')
        x_min: Minimum x value
        x_max: Maximum x value
    """
    try:
        x = np.linspace(x_min, x_max, 400)
        
        # Use a restricted locals dictionary to evaluate the function string securely
        allowed_locals = {
            "x": x,
            "np": np,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log,
            "sqrt": np.sqrt,
            "pi": np.pi,
            "e": np.e
        }
        
        y = eval(function_str, {"__builtins__": {}}, allowed_locals)
        
        plt.figure(figsize=(6, 4))
        plt.plot(x, y, label=function_str)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.legend()
        
        buf = io.StringIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        plt.close()
        
        return buf.getvalue()
    except Exception as e:
        return f"Error plotting function: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
