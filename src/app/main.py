import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis, ConnectionError

# import redis.asyncio as r

from app.exceptions.exceptions import AppExceptions
from app.logging.logg import logger, set_up_logging
from app.routers.v1 import router as v1_router

set_up_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before start

    app.state.redis = Redis(host="localhost", port=6379)

    try:
        await app.state.redis.ping()  # type: ignore
    except ConnectionError:
        logger.critical("Redis Connection Failed")
        raise

    yield
    #  SHUTDOWN of application
    await app.state.redis.flushdb()  # After each aplication run clear Redis DB
    await app.state.redis.aclose()  # close redis DB


app = FastAPI(lifespan=lifespan)

app.include_router(v1_router)


@app.exception_handler(
    AppExceptions,
)
async def app_exception_handler(request: Request, exception: AppExceptions):
    return JSONResponse(
        status_code=exception.status_code, content={"message": exception.message}
    )


@app.middleware("http")
async def add_loggin(request: Request, call_next):

    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    method = request.method

    with logger.contextualize(request_id=request_id):
        logger.info(f"Incoming {method} {request.url.path}")
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled exception during request")
            raise
        duration_ms = (time.perf_counter() - start_time) * 1000
        if response.status_code > 500:
            logger.error(f"ERROR {response.status_code} in {duration_ms:.2f}ms")
        else:
            logger.info(f"Completed {response.status_code} in {duration_ms:.2f}ms")
        return response


@app.get("/health")
def health_check() -> dict:
    return {"Status": "OK"}
