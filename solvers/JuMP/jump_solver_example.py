
import pyarrow as pa
from solvers.solver import BaseSolver

# Example solver taken from pyomo tutorial implementing base solver
class JumpSolverSample(BaseSolver):
    def __init__(self):
        super().__init__()
        pass
    
    # Run the solver
    def run(self, params:pa.Table) -> pa.Table:
        pass
