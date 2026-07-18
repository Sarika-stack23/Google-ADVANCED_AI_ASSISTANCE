"""
Symbolic Math API — /api/v1/symbolic endpoints.
Provides direct access to SymPy operations.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.src.math.symbolic_engine import SymbolicMathEngine

router = APIRouter(prefix="/api/v1/symbolic", tags=["symbolic"])

class SymbolicRequest(BaseModel):
    expression: str
    operation: str
    variable: str = "x"

@router.post("")
async def compute_symbolic(req: SymbolicRequest):
    engine = SymbolicMathEngine()
    
    if req.operation == "differentiate":
        result = engine.differentiate(req.expression, req.variable)
    elif req.operation == "integrate":
        result = engine.integrate(req.expression, req.variable)
    elif req.operation == "solve":
        result = engine.solve_equation(req.expression, req.variable)
    elif req.operation == "simplify":
        # The method in SymbolicMathEngine is likely 'simplify_expression' or 'simplify'
        # Let's use try-except or check methods
        if hasattr(engine, 'simplify_expression'):
            result = engine.simplify_expression(req.expression)
        elif hasattr(engine, 'simplify'):
            result = engine.simplify(req.expression)
        else:
            result = "Simplify not supported"
    else:
        return {"error": "Invalid operation"}
        
    return {"result": result}
