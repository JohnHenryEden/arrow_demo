from typing import Union, Annotated
import pyarrow as pa
import pyarrow.ipc as ipc
import io
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from objects.wrappers.mat_file import MatFile
from controller.endpoints import *

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/compute")
async def compute(file: Annotated[UploadFile, File()], file_path: Annotated[str, Form()]):
    contents = await file.read()
    
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {
            "file_size": len(contents),
            "filename": file.filename,
            "path": file_path
        }