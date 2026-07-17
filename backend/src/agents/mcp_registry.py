import os
import json
import asyncio
from typing import List
from langchain.tools import Tool
from backend.src.config import settings

def get_mcp_tools() -> List[Tool]:
    """Dynamically discover and return MCP tools."""
    tools = []
    
    if not getattr(settings, "USE_MCP", True):
        # Fallback to direct SymPy calls
        import sympy as sp
        from sympy.parsing.sympy_parser import parse_expr
        
        def fallback_differentiate(expr: str) -> str:
            return str(sp.diff(parse_expr(expr), sp.Symbol('x')))
            
        tools.append(Tool(
            name="differentiate",
            description="Calculate the derivative of a mathematical expression.",
            func=fallback_differentiate
        ))
        return tools

    # In a full production setup, this would use mcp.client.stdio.stdio_client to connect
    # to the 6 subprocesses. For latency and simplicity in this sandbox, we'll import
    # the server tool functions directly but wrap them as LangChain tools, simulating
    # an MCP Tool discovery registry.
    
    import sys
    import importlib.util
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../mcp-servers'))
    
    def load_module_from_path(module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
        
    try:
        sympy_mcp = load_module_from_path("sympy_mcp", os.path.join(base_dir, "sympy-mcp", "server.py"))
        calc_mcp = load_module_from_path("calculator_mcp", os.path.join(base_dir, "calculator-mcp", "server.py"))
        graph_mcp = load_module_from_path("graph_plotter_mcp", os.path.join(base_dir, "graph-plotter-mcp", "server.py"))
        pdf_mcp = load_module_from_path("pdf_reader_mcp", os.path.join(base_dir, "pdf-reader-mcp", "server.py"))
        exec_mcp = load_module_from_path("python_executor_mcp", os.path.join(base_dir, "python-executor-mcp", "server.py"))
        img_mcp = load_module_from_path("image_solver_mcp", os.path.join(base_dir, "image-solver-mcp", "server.py"))
        
        tools.extend([
            Tool(name="differentiate", description="Calculate derivative of expr in terms of x", func=lambda x: str(sympy_mcp.differentiate(x))),
            Tool(name="integrate", description="Calculate integral of expr in terms of x", func=lambda x: str(sympy_mcp.integrate(x))),
            Tool(name="simplify", description="Simplify mathematical expression", func=lambda x: str(sympy_mcp.simplify(x))),
            Tool(name="solve", description="Solve algebraic equation equal to 0", func=lambda x: str(sympy_mcp.solve(x))),
            Tool(name="execute_python", description="Execute sandboxed python code. Returns stdout.", func=exec_mcp.execute_python),
            Tool(name="plot_function", description="Plot a math function string into SVG", func=graph_mcp.plot_function),
            Tool(name="read_pdf", description="Read base64 PDF", func=pdf_mcp.read_pdf),
            Tool(name="extract_and_solve_image", description="Extract and solve math from base64 image", func=lambda x: str(img_mcp.extract_and_solve_image(x)))
        ])
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to load MCP tools: {e}")
        
    return tools
