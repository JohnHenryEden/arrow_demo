import uvicorn, multiprocessing
from arrow_rpc_server import grpc_serve_addr
import logging
import sys

# Run all servers in multiprocessing

port = 8000
grpc_port = 8100
ipaddr = "127.0.0.1"
def setup_custom_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(f'%(levelname)s:     %(message)s')
    handler.setFormatter(formatter)
    # Avoid adding multiple handlers if re-run
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

def run_server():
    logger = setup_custom_logger(f"worker_fastAPI")
    logger.info("Starting worker on FastAPI")
    uvicorn.run("fastapi_restful:app",
                host=ipaddr,
                port=port,
                reload=False,
                log_level="info",
                access_log=True)
def run_grpc_server():
    logger = setup_custom_logger(f"worker_grpc")
    logger.info("Starting worker on gRPC server")
    grpc_serve_addr(ipaddr, grpc_port, logger)
    
def start_all() -> None:
    server_thread = multiprocessing.Process(target=run_server, daemon=True)
    grpc_thread = multiprocessing.Process(target=run_grpc_server, daemon=True)
    server_thread.start()
    grpc_thread.start()
    server_thread.join()
    grpc_thread.join()

# Run script to start everything
if __name__ == "__main__":
    start_all()