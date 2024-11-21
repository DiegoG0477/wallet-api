from fastapi import APIRouter, Depends, Request
from src.controllers.financial_controller import FinancialController
from src.middlewares.auth_middleware import auth_middleware
from src.schemas.financial_schemas import (
    MetaAhorroCreate,
    MetaAhorro,
    CategoriaGastoCreate,
    CategoriaGastoGet,
    GastoCreate,
)
from typing import List

router = APIRouter(
    prefix="/financial",
    tags=["Financial"]
)

@router.post("/metas", response_model=dict, status_code=201, dependencies=[Depends(auth_middleware)])
def crear_meta_ahorro(meta_data: MetaAhorroCreate, request: Request):
    """
    Crear una nueva meta de ahorro.
    """
    usuario_id = request.state.user.id
    return FinancialController.crear_meta_ahorro(usuario_id, meta_data)

@router.patch("/metas/{meta_id}", response_model=dict, dependencies=[Depends(auth_middleware)])
def modificar_meta_ahorro(meta_id: str, meta_data: MetaAhorroCreate, request: Request):
    """
    Modificar una meta de ahorro existente.
    """
    usuario_id = request.state.user.id
    return FinancialController.modificar_meta_ahorro(usuario_id, meta_id, meta_data)

@router.delete("/metas/{meta_id}", response_model=dict, dependencies=[Depends(auth_middleware)])
def eliminar_meta_ahorro(meta_id: str, request: Request):
    """
    Eliminar una meta de ahorro existente.
    """
    usuario_id = request.state.user.id
    return FinancialController.eliminar_meta_ahorro(usuario_id, meta_id)

@router.get("/metas", response_model=List[MetaAhorro], dependencies=[Depends(auth_middleware)])
def obtener_metas_ahorro(request: Request):
    """
    Obtener todas las metas de ahorro de un usuario.
    """
    usuario_id = request.state.user.id
    return FinancialController.obtener_metas_ahorro(usuario_id)

@router.post("/categorias", response_model=dict, status_code=201, dependencies=[Depends(auth_middleware)])
def crear_categoria_gasto(categoria_data: CategoriaGastoCreate, request: Request):
    """
    Crear una nueva categoría de gasto.
    """
    usuario_id = request.state.user.id
    return FinancialController.crear_categoria_gasto(usuario_id, categoria_data)

@router.get("/categorias", response_model=List[CategoriaGastoGet], dependencies=[Depends(auth_middleware)])
def obtener_categorias_gasto(periodo: float, request: Request):
    """
    Obtener todas las categorías de gasto de un usuario y calcular el total gastado por categoría.
    """
    usuario_id = request.state.user.id
    return FinancialController.obtener_categorias_gasto(usuario_id, periodo)

@router.post("/gastos", response_model=dict, status_code=201, dependencies=[Depends(auth_middleware)])
def registrar_gasto(gasto_data: GastoCreate, request: Request):
    """
    Registrar un nuevo gasto.
    """
    usuario_id = request.state.user.id
    return FinancialController.registrar_gasto(usuario_id, gasto_data)

@router.post("/metas/{meta_id}/abono", response_model=dict, dependencies=[Depends(auth_middleware)])
def abonar_meta(meta_id: str, monto: float, request: Request):
    """
    Abonar a una meta de ahorro específica.
    """
    usuario_id = request.state.user.id
    return FinancialController.abonar_meta(usuario_id, meta_id, monto)