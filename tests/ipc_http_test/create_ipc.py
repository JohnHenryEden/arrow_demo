
import pyarrow as pa
import requests

# Upload the .mat file to server
url = "http://127.0.0.1:8000/saveModel"
mat_file_path = "sample\\e_coli_core.mat"
files = {
    'model': ('e_coli_core.mat', open(mat_file_path, 'rb'), 'text/plain')
}
params = {
    "model_name": "e_coli_core"
}
req = requests.post(url, files=files, data=params)
print(req.content)
