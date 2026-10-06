import logging

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from sqlalchemy import text

from app import models
from app.api.assets import router as assets_router
from app.api.auth import router as auth_router
from app.api.incident_users import router as incident_users_router
from app.api.indicators import router as indicators_router
from app.api.incidents import router as incidents_router
from app.api.simulations import router as simulations_router
from app.db.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="THE CLOCK IS RUNNING")

logger = logging.getLogger(__name__)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return concise field-level validation errors."""
    messages = []
    for error in exc.errors():
        fields = [
            str(part)
            for part in error["loc"]
            if part not in {"body", "query", "path", "header"}
        ]
        field = ".".join(fields) or "request"
        messages.append(f"{field}: {error['msg']}")
    return JSONResponse(status_code=422, content={"detail": "; ".join(messages)})


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Hide unexpected error details from API clients while logging them."""
    logger.exception("Unhandled application error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth_router)  # Register the authentication endpoints.
app.include_router(incidents_router)  # Register the incident CRUD endpoints.
app.include_router(indicators_router)  # Register the indicator endpoints.
app.include_router(assets_router)  # Register the affected asset endpoints.
app.include_router(incident_users_router)  # Register the affected user endpoints.
app.include_router(simulations_router)  # Register the simulation endpoints.

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def database_health(db=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}
