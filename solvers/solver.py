# Base solver
import pyarrow as pa

# Base class for all solvers
class BaseSolver:
    def __init__(self):
        pass

    def run(self, params:pa.Table) -> pa.Table:
        pass