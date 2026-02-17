from fastapi import FastAPI, Request
from app.exceptions.exceptions import AppExceptions
from app.routers.v1 import router as v1_router
from fastapi.responses import JSONResponse

app = FastAPI()
app.include_router(v1_router)


@app.exception_handler(
    AppExceptions,
)
async def app_exception_handler(request: Request, exception: AppExceptions):
    return JSONResponse(
        status_code=exception.status_code, content={"message": exception.message}
    )


@app.get("/health")
def health_check() -> dict:
    return {"Status": "OK"}
