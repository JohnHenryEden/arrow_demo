from solvers.solver import BaseSolver
from solvers.pyomo.glpk_solver_example import GlpkSolverSample

class SolverFactory:
    def __init__(self):
        pass
        
    def get_solver(self, name:str) -> BaseSolver:
        if name == "pyomo.glpk_solver_example":
            return GlpkSolverSample()
        pass