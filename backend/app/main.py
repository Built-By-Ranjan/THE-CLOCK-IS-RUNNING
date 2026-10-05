from fastapi import Depends, FastAPI
from sqlalchemy import text

from app import models
from app.api.simulations import router as simulations_router
from app.db.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="THE CLOCK IS RUNNING")
app.include_router(simulations_router)  # Register the simulation endpoints.

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def database_health(db=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}
