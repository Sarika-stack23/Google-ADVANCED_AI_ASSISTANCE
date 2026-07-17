from mcp.server.fastmcp import FastMCP
from RestrictedPython import compile_restricted
from RestrictedPython import safe_builtins
import sys
import io

mcp = FastMCP("Python Executor Server")

@mcp.tool()
def execute_python(code: str) -> str:
    """Execute Python code in a sandboxed environment.
    
    Args:
        code: The Python code to execute. Print statements will be captured and returned.
    """
    # Compile the code in a restricted environment
    byte_code = compile_restricted(code, '<inline code>', 'exec')
    
    # Setup safe globals
    from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
    
    class CustomPrintCollector:
        def __init__(self, _getattr_=None):
            self.txt = []
        def __call__(self, *args, **kwargs):
            print(*args, **kwargs)
            return self
        def _call_print(self, *args, **kwargs):
            print(*args, **kwargs)
            return ""
            
    # RestrictedPython uses _print_() to get a callable, then calls it, and assigns its return value to `printed`.
    def my_print_factory():
        def my_print(*args, **kwargs):
            print(*args, **kwargs)
            return ""
        return my_print

    safe_globals = {
        '__builtins__': safe_builtins,
        '_print_': CustomPrintCollector,
        '_getattr_': getattr,
        '_getitem_': lambda obj, key: obj[key],
        '_getiter_': iter,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
        '_write_': lambda obj: obj
    }
    
    # Capture stdout
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    try:
        # Execute
        exec(byte_code, safe_globals)
        return redirected_output.getvalue()
    except SyntaxError as e:
        return f"SyntaxError: {str(e)}"
    except Exception as e:
        if type(e).__name__ == "SecurityError" or "import" in str(e).lower() or "not allowed" in str(e).lower():
             return f"SecurityError: Execution blocked due to sandbox restrictions ({str(e)})"
        return f"Execution Error: {str(e)}"
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    mcp.run(transport='stdio')
