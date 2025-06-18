class EngineModel:
    def __init__(
        self,
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

        self.S = S
        self.S_row = S.column(S.schema.get_field_index("row"))
        self.S_col = S.column(S.schema.get_field_index("col"))
        self.S_data = S.column(S.schema.get_field_index("data"))

        self.b = b
        self.c = c
        self.lb = lb
        self.ub = ub
        self.osense = osense
        self.csense = csense
