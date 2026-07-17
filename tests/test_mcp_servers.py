import pytest
import os
import sys
import importlib.util

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../mcp-servers'))

sympy_mcp = load_module_from_path("sympy_mcp", os.path.join(base_dir, "sympy-mcp", "server.py"))
calc_mcp = load_module_from_path("calculator_mcp", os.path.join(base_dir, "calculator-mcp", "server.py"))
graph_mcp = load_module_from_path("graph_plotter_mcp", os.path.join(base_dir, "graph-plotter-mcp", "server.py"))
exec_mcp = load_module_from_path("python_executor_mcp", os.path.join(base_dir, "python-executor-mcp", "server.py"))

differentiate = sympy_mcp.differentiate
integrate = sympy_mcp.integrate
simplify = sympy_mcp.simplify
solve = sympy_mcp.solve

add = calc_mcp.add
subtract = calc_mcp.subtract
multiply = calc_mcp.multiply
divide = calc_mcp.divide

plot_function = graph_mcp.plot_function
execute_python = exec_mcp.execute_python

def test_sympy_mcp():
    res = differentiate("x**3")
    assert "3*x**2" in res.get("result", "")
    assert "3 x^{2}" in res.get("latex", "")
    
    res_int = integrate("3*x**2")
    assert "x**3" in res_int.get("result", "")

def test_calculator_mcp():
    assert add(2, 3) == 5
    assert subtract(10, 4) == 6
    assert multiply(3, 4) == 12
    assert divide(10, 2) == 5

def test_graph_plotter_mcp():
    svg = plot_function("np.sin(x)")
    assert "<svg" in svg
    assert "</svg>" in svg

def test_python_executor_mcp_security():
    # Should be blocked
    res = execute_python("import os\nos.system('echo hi')")
    assert "SecurityError" in res or "not allowed" in res
    
    # Should work
    res2 = execute_python("print(2 + 2)")
    assert "4" in res2
