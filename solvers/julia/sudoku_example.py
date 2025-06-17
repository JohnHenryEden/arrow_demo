from solvers.solver import BaseSolver
import pyarrow as pa
import pyarrow.cffi
import cffi

class SudokuExample(BaseSolver):
    def __init__(self):
        pass
    
    # using cffi and zero-copy the table to julia
    def run(self, params:pa.Table) -> pa.Table:
        
        ffi = cffi.FFI()
        c_array = ffi.new("struct ArrowArray*")
        c_schema = ffi.new("struct ArrowSchema*")
        # Export to Arrow C Data Interface
        pa.cffi.export_to_c(params, c_array, c_schema)
        
        pass