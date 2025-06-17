from solvers.solver import BaseSolver
from solvers.pyomo.glpk_solver_example import GlpkSolverSample
from solvers.julia.sudoku_example import SudokuExample

class SolverFactory:
    def __init__(self):
        pass
        
    def get_solver(self, name:str) -> BaseSolver:
        if name == "pyomo.glpk_solver_example":
            return GlpkSolverSample()
        if name == "julia.sudoku_example":
            return SudokuExample()
        pass