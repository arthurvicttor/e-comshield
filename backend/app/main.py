from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(
    title="E-ComShield API",
    description="Backend API for the E-ComShield system",
    version="0.1.0",
)


app.include_router(health_router)
from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.predict import router as predict_router
from sqlalchemy import text
from app.db.session import engine


app = FastAPI(
    title="E-ComShield API",
    description="Backend API for the E-ComShield system",
    version="0.1.0",
)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)
@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar()}