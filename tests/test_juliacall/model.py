from typing import Union
import numpy as np
import pyarrow as pa
from pyarrow import ipc
import io


class Model:
    def __init__(self, model_name, S, lb, ub, c, rxns, mets, osense, csense):
        self.model_name = model_name
        self.S = S  # Stoichiometric matrix
        self.lb = lb  # Lower bounds
        self.ub = ub  # Upper bounds
        self.c = c  # Objective coefficients
        self.rxns = rxns  # Reactions
        self.mets = mets  # Metabolites
        self.osense = osense  # Optimization sense ('max' or 'min')
        self.csense = csense  # Constraint sense
    
    
    @staticmethod
    def _bytes_helper(obj: Union[pa.Array, pa.RecordBatch, pa.Table]) -> bytes:
        # https://arrow.apache.org/docs/python/generated/pyarrow.ipc.new_stream.html#pyarrow.ipc.new_stream
        sink = io.BytesIO()

        if isinstance(obj, pa.Array):
            # new_stream() requires a schema, and pa.Array alone does not have a schema — only RecordBatch or Table do.
            batch = pa.record_batch({"field": obj})
        elif isinstance(obj, pa.RecordBatch):
            batch = obj
        elif isinstance(obj, pa.Table):
            # TODO: Handle Table serialization
            batch = obj.to_batches()[0] # stub: assuming single batch for simplicity
        else:
            raise TypeError("Unsupported type for Arrow serialization")

        with ipc.new_stream(sink, batch.schema) as writer:
            writer.write(batch)

        return sink.getvalue()

    
    def to_ipc_bytes(self):
        """
        Convert the model to Arrow IPC binary blocks for transmission.
        Returns:
            - A dictionary of Arrow IPC bytes:
                - "s": RecordBatch with columns ["row", "col", "data"]
                - "lb", "ub", "c": Arrow tables (1D)
                - "nrow", "ncol": inferred matrix shape
        """
        row = self.S["row"]
        col = self.S["col"]
        data = self.S["data"]

        # Estimate matrix dimensions from max index values in row/col
        # (since sparse matrix indices are 0-based, dimensions = max index + 1)
        nrow = int(pa.compute.max(row).as_py()) + 1
        ncol = int(pa.compute.max(col).as_py()) + 1

        S_batch = pa.record_batch({
            "row": row,
            "col": col,
            "data": data
        })
        
        S_shape_batch = pa.record_batch({
            "nrow": pa.array([nrow], type=pa.int64()),
            "ncol": pa.array([ncol], type=pa.int64())
        })

        return {
            "S": self._bytes_helper(S_batch),
            "lb": self._bytes_helper(self.lb),
            "ub": self._bytes_helper(self.ub),
            "c":  self._bytes_helper(self.c),
            "S_shape": self._bytes_helper(S_shape_batch)
        }
