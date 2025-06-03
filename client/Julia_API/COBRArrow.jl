module COBRArrowModule

using PyCall
using Arrow
using SparseArrays
using COBRA

export create_COBRArrow, load_model_from_flight_rpc, optimize_model

# Import the necessary Python modules
const pyarrow = pyimport_conda("pyarrow", "pyarrow")
const pyarrow_flight = pyimport_conda("pyarrow.flight", "libarrow-flight")
const numpy = pyimport_conda("numpy", "numpy")

# Define the struct
struct COBRArrow
    rpc_host::String
    rpc_port::Int
    client::PyObject
end

# Function to load the model from Arrow Flight RPC
function load_model_from_flight_rpc(service::COBRArrow, schemaName::String)
    # Fetching all necessary parts
    numpy_data_S = fetch_vector(service, "$(schemaName)_S")
    numpy_data_b = fetch_vector(service, "$(schemaName)_b")
    numpy_data_c = fetch_vector(service, "$(schemaName)_c")
    numpy_data_lb = fetch_vector(service, "$(schemaName)_lb")
    numpy_data_ub = fetch_vector(service, "$(schemaName)_ub")
    numpy_data_csense = fetch_vector(service, "$(schemaName)_csense")
    numpy_data_rxns = fetch_vector(service, "$(schemaName)_rxns")
    numpy_data_mets = fetch_vector(service, "$(schemaName)_mets")

    # Extract data from the numpy arrays
    row = convert(Vector{Int}, PyVector(numpy_data_S["row"]))
    col = convert(Vector{Int}, PyVector(numpy_data_S["col"]))
    val = convert(Vector{Float64}, PyVector(numpy_data_S["val"]))
    b = convert(Vector{Float64}, PyVector(numpy_data_b["b"]))
    c = convert(Vector{Float64}, PyVector(numpy_data_c["c"]))
    lb = convert(Vector{Float64}, PyVector(numpy_data_lb["lb"]))
    ub = convert(Vector{Float64}, PyVector(numpy_data_ub["ub"]))

    # Convert the data to Julia types
    csense_array = numpy_data_csense["csense"]
    csense_inner_array = csense_array[1]
    csense = [Char(x[1]) for x in csense_inner_array]

    rxns = convert(Vector{String}, PyVector(numpy_data_rxns["rxns"]))
    mets = convert(Vector{String}, PyVector(numpy_data_mets["mets"]))

    # Create the sparse matrix
    nrows = maximum(row)
    ncols = maximum(col)
    S = sparse(row, col, val, nrows, ncols)

    # osense
    # Initialize osense to handle scope issues
    osense = -2  # Default value
    try
        numpy_data_osense = fetch_vector(service, "$(schemaName)_osense")
        osense = Int8(numpy_data_osense["osense"][1])
    catch e
        try
            numpy_data_osenseStr = fetch_vector(service, "$(schemaName)_osenseStr")
            osenseStr = numpy_data_osenseStr["osenseStr"][1]
            if osenseStr == "max"
                osense = 1
                @info "The model objective is set to be maximized."
            elseif osenseStr == "min"
                osense = -1
                @info "The model objective is set to be maximized."
            else
                error("Invalid value for osenseStr: $osenseStr. Expected 'max' or 'min'.")
            end
        catch e
            osense = -1
            println("The model objective is set to be maximized.")
        end
    end

    # Check for additional constraints and combine if they exist
    try
        numpy_data_C = fetch_vector(service, "$(schemaName)_C")
        numpy_data_d = fetch_vector(service, "$(schemaName)_d")
        numpy_data_dsense = fetch_vector(service, "$(schemaName)_dsense")
        numpy_data_ctrs = fetch_vector(service, "$(schemaName)_ctrs")

        if !isempty(numpy_data_C) && !isempty(numpy_data_d)
            @info "This is a coupled model."
            row_C = convert(Vector{Int}, PyVector(numpy_data_C["row"]))
            col_C = convert(Vector{Int}, PyVector(numpy_data_C["col"]))
            val_C = convert(Vector{Float64}, PyVector(numpy_data_C["val"]))
            nrows_C = maximum(row_C)
            ncols_C = maximum(col_C)
            C = sparse(row_C, col_C, val_C, nrows_C, ncols_C)

            d = convert(Vector{Float64}, PyVector(numpy_data_d["d"]))
            ctrs = convert(Vector{String}, PyVector(numpy_data_ctrs["ctrs"]))

            dsense_array = numpy_data_dsense["dsense"]
            dsense_inner_array = dsense_array[1]
            dsense = [Char(x[1]) for x in dsense_inner_array]

            S = [S; C]
            b = [b; d]
            csense = [csense; dsense]
            mets = [mets; ctrs]
        end
    catch e
        println("No additional constraints found or an error occurred.")
    end


    return COBRA.LPproblem(S, b, c, lb, ub, osense, csense, rxns, mets)
end

# Method to optimize the model using the do_optimize action in the RPC server
function optimize_model(service::COBRArrow, schemaName::String, solverName::String="GLPK")
    # Convert the action body to bytes
    action_body_str = "{'schema_name': '$schemaName', 'solver_name': '$solverName'}"
    action_body = Vector{UInt8}(action_body_str)

    # Create the action
    action = pyarrow_flight.Action("optimize", action_body)
    # Call the action on the server

    result_stream = service.client.do_action(action)
    py_dict = Dict{String,PyObject}()

    for result in result_stream
        body = result.body
        buffer = pyarrow.BufferReader(body)
        try
            reader = pyarrow.ipc.RecordBatchStreamReader(buffer)
            table = reader.read_all()
            # Convert the PyArrow table to a dictionary directly in Julia
            table_dict = convert_pyarrow_table_to_numpy(table)
            py_dict = merge(py_dict, table_dict)
        catch e
            message = convert(String, body.to_pybytes())
            error("An error occurred: $message")
        end
    end

    objective_value = convert(Float64, py_dict["objective_value"][1])
    flux = convert(Vector{Float64}, PyVector(py_dict["flux"]))
    status = convert(String, py_dict["status"][1])
    rxns = convert(Vector{String}, PyVector(py_dict["rxns"]))

    result_dict = Dict("objective_value" => objective_value, "status" => status, "rxns" => rxns, "flux" => flux)
    return result_dict

end

# Constructor for the struct
function create_COBRArrow(host::String, port::Union{Int,Nothing}=nothing)
    client = if isnothing(port)
        pyarrow_flight.FlightClient("grpc://$host")
    else
        pyarrow_flight.FlightClient("grpc://$host:$port")
    end
    return COBRArrow(host, port, client)
end

# Function to fetch a vector from the Arrow Flight RPC
function fetch_vector(service::COBRArrow, key::String)
    client = service.client
    descriptor = pyarrow_flight.FlightDescriptor.for_command(key)
    try
        flight_info = client.get_flight_info(descriptor)
        flight_endpoint = flight_info.endpoints[1]
        flight_reader = client.do_get(flight_endpoint.ticket)
        flight_data = nothing
        try
            flight_data = flight_reader.read_all()
        catch e
            all_chunks = pyimport("builtins").list()
            while true
                try
                    chunk = flight_reader.read_chunk()
                    if isempty(chunk)
                        break
                    end
                    push!(all_chunks, chunk.data)   #Collect each chunk as Arrow RecordBatch
                catch e
                    break
                end
            end
            flight_data = pyarrow.Table.from_batches(all_chunks)
        end
        # # Convert the Arrow table to a dictionary of numpy arrays
        data_dict = convert_pyarrow_table_to_numpy(flight_data)
        return data_dict
    catch e
        # Handle the specific ArrowKeyError
        if isa(e, PyCall.PyError) && occursin("ArrowKeyError", string(e))
            error("KeyError: Flight not found for key: $key")
        else
            rethrow(e)
        end
    end
end

function convert_pyarrow_table_to_numpy(table::PyObject)
    data_dict = Dict{String,PyObject}()
    for column in table.schema.names
        column_data = table.column(column)
        data_dict[column] = numpy.array(column_data, copy=true)  # Ensure writable copy
    end
    return data_dict
end

end # module
