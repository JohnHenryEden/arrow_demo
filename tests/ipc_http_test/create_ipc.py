
import pyarrow as pa
import requests

BATCH_SIZE = 10000

NUM_BATCHES = 1000

ARROW_STREAM_FORMAT = 'application/vnd.apache.arrow.stream'
schema = pa.schema([pa.field('nums', pa.int32())])

# with pa.OSFile('bigfile.arrow', 'wb') as sink:
#     with pa.ipc.new_file(sink, schema) as writer:
#         for row in range(NUM_BATCHES):
#             batch = pa.record_batch([pa.array(range(BATCH_SIZE), type=pa.int32())], schema)
#             writer.write(batch)
            
with pa.memory_map('bigfile.arrow', 'rb') as source:
    url = 'http://127.0.0.1:8000/read_ipc'
    loaded_array = pa.ipc.open_file(source).read_all()
    print("Reading IPC successful, LEN:", len(loaded_array))
    req = requests.post(url, data = loaded_array, headers={
        "Content-Type": ARROW_STREAM_FORMAT
    })
    print(req)

