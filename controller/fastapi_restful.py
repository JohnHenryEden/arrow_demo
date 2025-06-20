from typing import Union, Annotated
import pyarrow as pa
import pyarrow.ipc as ipc
import io
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from controller.endpoints import *
from objects.engine_model import EngineModel

app = FastAPI()
endpoint = Endpoint()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/compute")
async def compute(model: Annotated[UploadFile, File(), None] = None,
            model_name: Annotated[str, None] = Form(...),
            engine: Annotated[str, None] = Form(...),
            solver: Annotated[str, None] = Form(...)):
    contents = await model.read()
    # handle model saving logic
    endpoint.compute(payload={
        "model_name": model_name,
        "engine": engine,
        "solver": solver,
        "model": contents
    })
    # handle compute logic
    return {"message": f"Computing model {model_name} successful"}


@app.post("/saveModel")
async def save(model_id: Annotated[str, None] = Form(...), 
            model_name: str = Form(...), 
            model: Annotated[UploadFile, File(), None] = None):
    contents = await model.read()
    
    mat_model = endpoint.parse_model(contents)
    aa = mat_model.to_ipc_bytes()
    print(f"Parsed model: {aa}")
    # handle model saving logic
    endpoint.save_model(payload={
        "model_id": model_id,
        "model_name": model_name,
        "model": contents
    })
    return {"message": f"Saving model {model_name} successful, file size: {len(contents)}"}