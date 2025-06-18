from typing import Union, Annotated
import pyarrow as pa
import pyarrow.ipc as ipc
import io
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from controller.endpoints import *

app = FastAPI()
endpoint = Endpoint()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/compute")
async def compute(model_id: Annotated[str, None] = None, 
            model: Annotated[UploadFile, File(), None] = None,
            data_name: Annotated[str, None] = None, 
            data_id: Annotated[str, None] = None, 
            data: Annotated[dict, None] = None):
    contents = await model.read()
    # handle model saving logic
    endpoint.compute(payload={
        "model_id": model_id,
        "data_id": data_id,
        "data_name": data_name,
        "data": data,
        "model": contents
    })
    # handle compute logic
    return {"message": f"Computing model {model_id} successful"}


@app.post("/saveModel")
async def save(model_id: Annotated[str, None] = None, 
            model_name: str = "Model", 
            model: Annotated[UploadFile, File(), None] = None):
    contents = await model.read()
    # handle model saving logic
    endpoint.save_model(payload={
        "model_id": model_id,
        "model_name": model_name,
        "model": contents
    })
    return {"message": f"Saving model {model_name} successful, file size: {len(contents)}"}