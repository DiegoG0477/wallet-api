from pydantic import BaseModel, Field
from src.schemas.user_schemas import UsuarioBase
from typing import Optional

class Login(BaseModel):
    correo: str
    contrasena: str

class Register(UsuarioBase):
    salario_mxn: Optional[float] = Field(None, description="Salario en MXN o null si no aplica")
    salario_usd: Optional[float] = Field(None, description="Salario en USD o null si no aplica")
    balance_objetivo: float = Field(..., description="Meta de balance financiero del usuario")
    gasto_limite: float = Field(..., description="Límite de gasto mensual del usuario")

class Token(BaseModel):
    access_token: str
    token_type: str