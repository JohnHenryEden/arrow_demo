
import pyarrow as pa
import requests

# Upload the .mat file to server
url = "http://127.0.0.1:8000/compute"
mat_file_path = "sample\\e_coli_core.mat"
files = {
    'file': ('e_coli_core.mat', open(mat_file_path, 'rb'), 'text/plain')
}
params = {
    "file_path": mat_file_path
}
req = requests.post(url, files=files, data=params)
print(req.content)
