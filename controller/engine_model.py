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
        if not isinstance(S, pa.RecordBatch):
            raise TypeError("S must be a pyarrow RecordBatch")

        for name in ["row", "col", "data"]:
            if name not in S.schema.names:
                raise ValueError(f"S must contain column '{name}'")

        self.model_name = model_name
        self.S = S
        self.b = b
        self.c = c
        self.lb = lb
        self.ub = ub
        self.osense = osense
        self.csense = csense


    @staticmethod
    def _bytes_helper(table: pa.Table) -> bytes:
        sink = io.BytesIO()
        with ipc.new_stream(sink, table.schema) as w:
            w.write_table(table)
        return sink.getvalue()


    def to_ipc_bytes(self):
        """
        Convert the model to Arrow IPC binary blocks for transmission.
        Returns:
            - A dictionary of Arrow IPC bytes:
                - "S": RecordBatch with columns ["row", "col", "data"]
                - "lb", "ub", "c": Arrow tables (1D)
            - nrow, ncol: dimensions (inferred from S if possible)
        """
        # 提取 S 中 row, col, data 三列
        row = self.S["row"]
        col = self.S["col"]
        data = self.S["data"]

        # 确保可以推断矩阵大小（假设最大索引 + 1）
        nrow = int(pa.compute.max(row).as_py()) + 1
        ncol = int(pa.compute.max(col).as_py()) + 1

        # 封装为一个 RecordBatch
        S_batch = pa.record_batch({
            "row": row,
            "col": col,
            "data": data
        })

        # 各字段转换为 Arrow IPC 二进制
        return {
            "S": self._bytes_helper(S_batch),
            "lb": self._bytes_helper(pa.table({"lb": self.lb})),
            "ub": self._bytes_helper(pa.table({"ub": self.ub})),
            "c":  self._bytes_helper(pa.table({"c":  self.c})),
            "nrow": nrow,
            "ncol": ncol
        }
        
        
    