from pydantic import BaseModel, Field
from src.schemas.user_schemas import UsuarioBase
from typing import Literal

class Login(BaseModel):
    correo: str
    contrasena: str

class Register(UsuarioBase):
    salario: float
    divisa: Literal["MXN", "USD"]
    balance_objetivo: float = Field(..., description="Meta de balance financiero del usuario")
    gasto_limite: float = Field(..., description="Límite de gasto mensual del usuario")

class Token(BaseModel):
    access_token: str
    token_type: str