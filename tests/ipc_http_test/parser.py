
import pyarrow as pa
import pyarrow.compute as pc
import requests

test_array = pa.array([1, 2, 3, 4, 5], type=pa.int64())
max_value = pc.max(test_array)
print(f"Max value in test_array: {max_value.as_py()}")

# Upload the .mat file to server
url = "http://127.0.0.1:8000/saveModel"
mat_file_path = "../sample/e_coli_core.mat"
files = {
    'model': ('e_coli_core.mat', open(mat_file_path, 'rb'), 'text/plain')
}
params = {
    "model_name": "e_coli_core"
}
req = requests.post(url, files=files, data=params)
print(req.content)
