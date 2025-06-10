# Calling Pyomo solvers via Apache arrow flight demo

Demonstration of calling a simple `glpk` solver running in `pyomo`

Dependency listed in `requirements.txt`, install using `pip install -r requirements.txt`

Using virtual environment is recommended.

Run `arrow_rpc_server.py` then `arrow_rpc_client.py`, the expected result is like this:

```json
            Item Value
0   Total Weight  12.0
1  Total Benefit  25.0
2         hammer   Yes
3         wrench    No
4    screwdriver   Yes
5          towel   Yes
```