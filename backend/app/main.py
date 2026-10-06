from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.database import init_db
from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.simulations import router as simulations_router
from app.api.ai import router as ai_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist in database
    try:
        init_db()
    except Exception as e:
        # If database connection fails on startup (e.g. Postgres not yet reachable), log and continue
        print(f"[WARN] Database initialization notice: {e}")
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-demo ready Core Incident Response Backend with 72-Hour Clock, Brute Force & Phishing Simulations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers ensuring no raw stack traces are exposed
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred while processing the request.",
        },
    )


# Health endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {"status": "ok"}


# Mount routers
app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(simulations_router)
app.include_router(ai_router)

