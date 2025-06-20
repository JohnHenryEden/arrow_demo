
import pyarrow as pa
import pyarrow.ipc as ipc
import requests

def mat_test():
    # Upload the .mat file to server
    url = "http://127.0.0.1:8000/compute"
    mat_file_path = "sample\\e_coli_core.mat"
    files = {
        'model': ('e_coli_core.mat', open(mat_file_path, 'rb'), 'text/plain'),
    }
    params = {
        "model_name": "e_coli_core",
        "engine": "pyomo",
        "solver": "cobra_lp"
    }
    req = requests.post(url=url, files=files, data=params)
    print(req.content)