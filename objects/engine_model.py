import pyarrow as pa
from pyarrow import ipc
import pyarrow.compute as pc
import io
from typing import Union

class EngineModel:
    def __init__(
        self,
        model_name: str,
        S: pa.RecordBatch,
        b: pa.Array,
        c: pa.Array,
        lb: pa.Array,
        ub: pa.Array,
        osense: pa.Scalar,
        csense: pa.Array
    ):
        # Ensure that S is a valid RecordBatch
        if not isinstance(S, pa.RecordBatch):
            raise TypeError("S must be a pyarrow RecordBatch")

        # Ensure that required columns exist in S: row indices, column indices, and data
        for name in ["row", "col", "data"]:
            if name not in S.schema.names:
                raise ValueError(f"S must contain column '{name}'")

        self.model_name = model_name
        self.S = S            # Sparse matrix in COO format (row, col, data)
        self.b = b            # Right-hand side vector
        self.c = c            # Objective function coefficients
        self.lb = lb          # Lower bounds
        self.ub = ub          # Upper bounds
        self.osense = osense  # Objective sense (e.g., "max" or "min")
        self.csense = csense  # Constraint senses (e.g., ["E", "L", "G"])

    @staticmethod
    def _bytes_helper(obj: Union[pa.Array, pa.RecordBatch, pa.Table]) -> bytes:
        """
        Helper method to convert a PyArrow object with schema(RecordBatch or Table)
        into Arrow IPC bytes using pyarrow.ipc.new_stream().
        https://arrow.apache.org/docs/python/generated/pyarrow.ipc.new_stream.html#pyarrow.ipc.new_stream
        """
        sink = io.BytesIO()

        if isinstance(obj, pa.Scalar):
            batch = pa.record_batch({"scalar": pa.array([obj])})
        elif isinstance(obj, pa.Array):
            # new_stream() requires a schema, and pa.Array alone does not have a schema — only RecordBatch or Table do.
            batch = pa.RecordBatch.from_pydict({"field": obj})
        elif isinstance(obj, pa.RecordBatch):
            batch = obj
        elif isinstance(obj, pa.Table):
            # NOTE: Currently not using table so assuming single batch for simplicity
            batch = obj.to_batches()[0] 
        else:
            print(f"Unsupported type for Arrow serialization: {type(obj)}")
            print(f"Object: {obj}")
            raise TypeError("Unsupported type for Arrow serialization")

        # Serialize the batch into IPC stream format
        with ipc.new_stream(sink, batch.schema) as writer:
            writer.write(batch)

        return sink.getvalue()       
        

    def to_pydict(self):
        """
        Convert the model to Arrow IPC binary blocks for transmission.
        Returns:
            A dictionary mapping each component name to its serialized Arrow IPC bytes:
                - "S":     Sparse matrix in COO format (RecordBatch with "row", "col", "data")
                - "S_shape": RecordBatch with matrix shape: "nrow", "ncol"
                - "b", "c", "lb", "ub", "csense": RecordBatches
                - "osense": Scalar (wrapped and serialized)
        """
        row = self.S["row"]
        col = self.S["col"]
        data = self.S["data"]

        # Estimate matrix dimensions from max index values in row/col
        # (since sparse matrix indices are 0-based, dimensions = max index + 1)
        nrow = int(pc.max(row).as_py()) + 1
        ncol = int(pc.max(col).as_py()) + 1

        # 封装为一个 RecordBatch
        S_batch = pa.record_batch({
            "row": row,
            "col": col,
            "data": data
        })
        
        S_shape_batch = pa.record_batch({
            "nrow": pa.array([nrow], type=pa.int64()),
            "ncol": pa.array([ncol], type=pa.int64())
        })

        # 各字段转换为 Arrow IPC 二进制
        return {
            "S": self._bytes_helper(S_batch),
            "lb": self._bytes_helper(self.lb),
            "ub": self._bytes_helper(self.ub),
            "b": self._bytes_helper(self.b),
            "c":  self._bytes_helper(self.c),
            "osense": self._bytes_helper(self.osense),
            "csense": self._bytes_helper(self.csense),
            "S_shape": self._bytes_helper(S_shape_batch)
        }
    
        
        
    