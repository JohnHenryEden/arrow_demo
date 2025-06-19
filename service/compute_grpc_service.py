"""
Service class that acts as a websocket/gRPC client between gateway and 
"""
from service.base_service import BaseService
import pyarrow as pa

class GrpcComputeService(BaseService):
    def __init__(self):
        self.gRPC_ip = "127.0.0.1"
        self.gRPC_port = 8815
        super().__init__()
    
    def compute(self, data: pa.RecordBatch = None):
        client = pa.flight.connect(f"grpc://{self.gRPC_ip}:{self.gRPC_port}")
        # Upload a new dataset(test data)
        data_dict = {
            "A": ['hammer', 'wrench', 'screwdriver', 'towel'],
            "b": [8, 3, 6, 11],
            "w": [5, 7, 4, 3],
            "W_max": 14
        }
        data_table = pa.RecordBatch.from_pydict(data_dict)

        upload_descriptor = pa.flight.FlightDescriptor.for_path("python_glpk_param")
        writer, _ = client.do_put(upload_descriptor, data_table.schema)
        writer.write_table(data_table)
        writer.close()


        # Retrieve metadata of newly uploaded dataset
        flight = client.get_flight_info(upload_descriptor)
        descriptor = flight.descriptor

        # Read content of the dataset
        reader = client.do_get(flight.endpoints[0].ticket)
        read_table = reader.read_all()

        # Drop the newly uploaded dataset

        result_reader = client.do_get(pa.flight.Ticket(b"do_solver,python_glpk_param,pyomo.glpk_solver_example"))
        client.do_action(pa.flight.Action("drop_dataset", "python_glpk_param".encode('utf-8')))

        print(result_reader.read_all().to_pandas())

# testing
if __name__ == "__main__":
    service = GrpcComputeService()
    service.compute()