from typing import Union
import pyarrow as pa
import pyarrow.ipc as ipc
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/read_ipc")
def read_ipc(item_id: int, q: Union[str, None] = None):
    sink = io.BytesIO()
    with ipc.new_file(sink, table.schema) as writer:
        for batch in table.to_batches():
            writer.write(batch)
    sink.seek(0)
    return StreamingResponse(
        generate_bytes(schema, batches),
        media_type="application/vnd.apache.arrow.stream"
    )