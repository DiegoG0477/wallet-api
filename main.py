from fastapi import FastAPI
import uvicorn

from src.models import user_models
from src.db.postgresql.config import engine
from src.routers.auth_router import router as auth_router
from src.routers.financial_router import router as financial_router

user_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(financial_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)