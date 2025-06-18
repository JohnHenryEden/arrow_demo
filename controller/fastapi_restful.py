from typing import Union, Annotated
import pyarrow as pa
import pyarrow.ipc as ipc
import io
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from objects.wrappers.mat_file import MatFile

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/compute")
def compute(upload_file: Annotated[UploadFile, File()],file_path: Annotated[str, Form()]):
    if not upload_file:
        return {"message": "No upload file sent"}
    else:
        return {
            "file_size": len(upload_file),
            "filename": file_path
        }