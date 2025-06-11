import pathlib

import pyarrow as pa
import pyarrow.flight
import pyarrow.parquet
from solvers.solver_factory import SolverFactory

solver_factory = SolverFactory()

class FlightServer(pyarrow.flight.FlightServerBase):

    def __init__(self, location="grpc://0.0.0.0:8815",
                repo=pathlib.Path("./datasets"), **kwargs):
        super(FlightServer, self).__init__(location, **kwargs)
        self._location = location
        self._repo = repo
        self._tables = {}

    def _make_flight_info(self, dataset):
        table = self._tables[dataset]
        schema = table.schema
        descriptor = pa.flight.FlightDescriptor.for_path(
            dataset.encode('utf-8')
        )
        endpoints = [pa.flight.FlightEndpoint(dataset, [self._location])]
        return pyarrow.flight.FlightInfo(schema,
                                        descriptor,
                                        endpoints,-1,-1)

    def list_flights(self, context, criteria):
        for dataset in self._repo.iterdir():
            yield self._make_flight_info(dataset.name)

    def get_flight_info(self, context, descriptor):
        return self._make_flight_info(descriptor.path[0].decode('utf-8'))

    def do_put(self, context, descriptor, reader, writer):
        dataset = descriptor.path[0].decode('utf-8')
        data_table = reader.read_all()
        self._tables[dataset] = data_table

    def do_get(self, context, ticket):
        ticket_str:str = ticket.ticket.decode()
        # handle do solvers
        if ticket_str.find("do_solver") != -1:
            return self.do_solver(ticket_str)
        # default endpoint
        else:
            dataset = ticket.ticket.decode('utf-8')
            return pa.flight.RecordBatchStream(self._tables[dataset])

    def list_actions(self, context):
        return [
            ("drop_dataset", "Delete a dataset."),
        ]

    def do_action(self, context, action):
        if action.type == "drop_dataset":
            return self.do_drop_dataset(action.body.to_pybytes().decode('utf-8'))
        elif action.type == "do_solver":
            return self.do_solver(action.body.to_pybytes().decode('utf-8'))
        else:
            raise NotImplementedError

    def do_drop_dataset(self, dataset):
        self._tables[dataset] = None
    # Execute a solver
    def do_solver(self, param:str):
        params = param.split(',')
        dataset = params[1]
        solver_name = params[2]
        # get data from memory
        input_params = self._tables[dataset]
        # get solver
        solver = solver_factory.get_solver(solver_name)
        # run solver and get result in form of pa table
        result = solver.run(input_params)
        # print results
        print(result.to_pandas())
        return pa.flight.RecordBatchStream(result)

if __name__ == '__main__':
    server = FlightServer()
    server._repo.mkdir(exist_ok=True)
    print("Server running at", server._location)
    server.serve()