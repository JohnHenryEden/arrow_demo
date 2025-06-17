# test_juliacall

This project demonstrates calling Julia from Python to solve an LP (FBA) model using JuMP.

## Dependencies
Install required Python packages:

```pip install -r requirements.txt```

## Overview

- **Model**: Uses the `e_coli_core.mat` metabolic model.
- **Python Components**:
  - `io_utils.py`: Loads the `.mat` file and extracts required computational fields.
  - `model.py`: Defines a `Model` class that stores FBA data and serializes it to Arrow IPC bytes.
  - `optimize.py`: Main entry point. Calls Julia to solve the model using `solve_julia.jl`.
- **Julia Components**:
  - `solve_julia.jl`: Accepts Arrow-serialized LP data from Python, deserializes it into Julia, and solves it using JuMP + a solver (e.g., HiGHS).
  - A `get_from_python()` function is used to receive and reconstruct the LP problem from Python.
  - `load.jl`: helps in loading model and testing Julia optimization directly(not call from Python)

## Usage
```
python optimize.py
```
This will:
- Load the e_coli model.
- Serialize it to Arrow IPC bytes.
- Invoke Julia script (solve_julia.jl) using JuliaCall.
- Trigger JuMP optimization.

## Known Issue
When Julia optimization starts via optimize.py, Python crashes with a segmentation fault.

This is not due to a bug in the Julia optimization logic itself, there are some commented code in solve_julia.jl that can be run directly in Julia, it works and returns a valid result.

The issue likely lies in how Julia is embedded or invoked from Python (possibly memory overflow).

