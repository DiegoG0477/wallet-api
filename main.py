from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.db.mongodb.config import mongo_connection
from src.models import user_models
from src.db.postgresql.config import engine
from src.routers.auth_router import router as auth_router
from src.routers.financial_router import router as financial_router
from src.routers.geo_router import router as geo_router

user_models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_connection.connect()
    yield  # Punto en el que la aplicación está corriendo
    await mongo_connection.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(financial_router)
app.include_router(geo_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)