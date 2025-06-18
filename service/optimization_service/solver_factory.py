from service.optimization_service.solver import BaseSolver
from service.optimization_service.pyomo.glpk_solver_example import GlpkSolverSample

class SolverFactory:
    def __init__(self):
        pass
        
    def get_solver(self, name:str) -> BaseSolver:
        if name == "pyomo.glpk_solver_example":
            return GlpkSolverSample()
        # TODO do something about julia
        pass