import uvicorn
import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, filename="../../logs/runtimeLog.log", filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

if __name__ == "__main__":
    logging.info("Starting the API server")
    uvicorn.run(app, host="127.0.0.1", port=7272)