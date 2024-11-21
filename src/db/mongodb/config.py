from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache
from pydantic_settings import BaseSettings  # Cambiado
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")

def get_database_name():
    return os.getenv("MONGO_DB_NAME", "mi_base_de_datos")

class MongoDBSettings(BaseSettings):
    MONGO_URI: str = get_database_url()
    MONGO_DB_NAME: str = get_database_name()

@lru_cache
def get_mongo_settings() -> MongoDBSettings:
    return MongoDBSettings()

class MongoDBConnection:
    def __init__(self):
        self._client = None
        self._db = None

    async def connect(self):
        """Inicia la conexión con MongoDB."""
        settings = get_mongo_settings()
        self._client = AsyncIOMotorClient(settings.MONGO_URI)
        self._db = self._client[settings.MONGO_DB_NAME]

    async def close(self):
        """Cierra la conexión con MongoDB."""
        self._client.close()

    @property
    def database(self):
        """Devuelve la referencia de la base de datos."""
        if not self._db:
            raise RuntimeError("La conexión no está inicializada. Llama a 'connect' primero.")
        return self._db

mongo_connection = MongoDBConnection()