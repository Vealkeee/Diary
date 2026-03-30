import uvicorn
import logging

from fastapi import FastAPI

from middleware.RateLimit import RateLimitMiddleware
from endpoints.getStudent import router as getStudent

logging.basicConfig(level=logging.INFO, filename="./logs/runtimeLog.log", filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

app.add_middleware(RateLimitMiddleware)
app.include_router(getStudent)

if __name__ == "__main__":
    try:
        logging.info("Starting the API server")
        uvicorn.run(app, host="127.0.0.1", port=7272)
    except Exception as e:
        logging.error(f"An error occurred while starting or developing the API server: {e}")