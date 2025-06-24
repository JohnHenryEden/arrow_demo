"""
Service class that acts as a gRPC client between gateway and engine gRPC service
"""
from service.base_service import BaseService
import pyarrow as pa
import json
from pyarrow import json as pajson
import pyarrow.flight
from utils.mat_parser import load_model_from_mat

class GrpcComputeService(BaseService):
    def __init__(self):
        self.gRPC_ip = "127.0.0.1"
        self.gRPC_port = 8101
        super().__init__()
    
                    
    def compute(self, model_bin = None) -> pa.Table:
        client = pa.flight.connect(f"grpc://{self.gRPC_ip}:{self.gRPC_port}")
        # Upload a new dataset(test data)
        data = load_model_from_mat(model_bin)
        ipc = data.__dict__
        for k, v in ipc.items():
            upload_descriptor = pa.flight.FlightDescriptor.for_path(f"cobra_lp_params:{k}")
            value = v
            # Convert pa array to batchTable
            if isinstance(v, pa.Array):
            # new_stream() requires a schema, and pa.Array alone does not have a schema — only RecordBatch or Table do.
                value = pa.RecordBatch.from_pydict({k: v})
            if isinstance(v, pa.Scalar):
            # new_stream() requires a schema, and pa.Array alone does not have a schema — only RecordBatch or Table do.
                value = pa.RecordBatch.from_pydict({k: [v.as_py()]})
            if value is not None and hasattr(value, "schema"):
                writer, reader = client.do_put(upload_descriptor, value.schema)
                if isinstance(value, pa.RecordBatch):
                    writer.write_batch(value)
                elif isinstance(value, pa.Table):
                    writer.write_table(value)
                writer.close()
            else:
                print(value)

        # Compute the model and drop dataset from gRPC server
        result_reader = client.do_get(pa.flight.Ticket(b"do_solver,cobra_lp_params,pyomo.cobra_lp"))
        client.do_action(pa.flight.Action("drop_dataset", "cobra_lp_params".encode('utf-8')))

        return result_reader.read_all()
