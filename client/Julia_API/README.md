## Instructions for Using Julia API

### Important Note
Please be aware that the Julia API is still under development, and as such, you may encounter issues when using it. 

### Step 1: Install Julia

1. **Download Julia**: Go to the [official Julia website](https://julialang.org/downloads/) and download the installer for your operating system.
2. **Install Julia**: Follow the installation instructions provided on the download page.

### Step 2: Instantiate the Julia Environment

1. **Open Julia REPL**: Start the Julia REPL by running `julia` from your terminal or command prompt.
      ```sh
     julia
     ```
2. **Create and Activate a Julia Environment**:
   ```julia
   julia> using Pkg
   julia> Pkg.add("PyCall")
   julia> Pkg.add("Arrow")
   ```

3. **Install CPLEX**:
   - Download and install CPLEX from the [IBM website](https://www.ibm.com/products/ilog-cplex-optimization-studio).
   - Set the CPLEX environment variable in Julia:
     ```julia
     julia> ENV["CPLEX_STUDIO_BINARIES"] = "path_to_CPLEX_runtime_binaries"
     ```
     Example:
     ```julia
     julia> ENV["CPLEX_STUDIO_BINARIES"] = "/Applications/CPLEX_Studio_Community2211/cplex/bin/arm64_osx" # Change to your path accordingly
     ```

4. **Install COBRA and CPLEX Packages**:
   ```julia
   julia> Pkg.add("CPLEX")
   julia> Pkg.add("COBRA")
   ```

5. **Install Conda and Additional Packages**:
   ```julia
   julia> Pkg.add("Conda")
   julia> using Conda
   julia> Conda.add("pyarrow")
   julia> Conda.add("libarrow-flight")
   ```

### Step 3: Example Usage of COBRArrow Module

**Run the Julia Script in Terminal**:
   - Create a Julia script (`test.jl`).
      ```julia
     # Create the service
      service = create_COBRArrow("localhost", 50051)

      # Define the schema name
      schemaName = "Recon3D"

      # Load the model
      model_from_flight = load_model_from_flight_rpc(service, schemaName)

      # optimize the model
      result = optimize_model(service, schemaName, "GLPK")
     ```
   - Run Julia script:
     ```sh
     julia test.jl
     ```