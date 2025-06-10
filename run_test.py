
import pyomo.environ as pyo
from solvers.pyomo.glpk_solver_example import GlpkSolverSample

glpk_solver_example = GlpkSolverSample()
result = glpk_solver_example.glpk_solver_example()

print(result.to_pandas())