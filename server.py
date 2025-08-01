from contextlib import asynccontextmanager

import joblib
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api import routes
from api.controllers import FraudsController
from api.services import FraudsService
from lib.common import logger
from lib.config import settings
from lib.repositories import FraudRepository

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Loading model weights", extra={"path": settings.MODEL_WEIGHT_PATH})
        data = joblib.load(settings.MODEL_WEIGHT_PATH)
        model = data["model"]

        repo = FraudRepository(database_url=settings.DATABASE_URL)
        service = FraudsService(
            repository=repo,
            model=model,
            feature_cols=settings.FEATURE_COLS,
        )
        controller = FraudsController(service)
        app.state.fraud_controller = controller

        logger.info(
            "Service and Controller initialized",
            extra={
                "features": settings.FEATURE_COLS,
                "database_url": settings.DATABASE_URL,
            },
        )
        yield

    except Exception:
        logger.exception("Error during startup")
        raise
    finally:
        logger.info("Application shutdown complete")


app = FastAPI(
    title="Fraud Detection System Service API",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    contact={"name": "Kiattiphum Suwanarsa"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def log_requests(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", "")
    logger.info(
        "→ Request start",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host,
            "request_id": req_id,
        },
    )
    response = await call_next(request)
    logger.info(
        "← Request end",
        extra={
            "status_code": response.status_code,
            "method": request.method,
            "url": str(request.url),
            "request_id": req_id,
        },
    )
    return response


app.include_router(routes.swagger_router)
app.include_router(routes.frauds_router, prefix=API_PREFIX)


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=False,
    )
