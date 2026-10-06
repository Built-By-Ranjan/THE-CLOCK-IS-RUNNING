from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.simulations import router as simulations_router

__all__ = ["auth_router", "incidents_router", "simulations_router"]
