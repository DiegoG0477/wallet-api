from fastapi import APIRouter, Depends, Request
from src.controllers import financial_controller
from src.middlewares.auth_middleware import auth_middleware
from src.schemas.financial_schemas import (
    MetaAhorroCreate,
    MetaAhorroBase,
    MetaAhorro,
    CategoriaGastoCreate,
    CategoriaGasto,
    GastoCreate,
)
from typing import List

router = APIRouter(
    prefix="/financial",
    tags=["Financial"]
)

@router.post("/metas", response_model=dict, status_code=201, dependencies=[Depends(auth_middleware)])
async def crear_meta_ahorro(meta_data: MetaAhorroCreate, request: Request):
    """
    Crear una nueva meta de ahorro.
    """
    usuario_id = request.state.user.id
    response = await financial_controller.crear_meta_ahorro(usuario_id, meta_data)
    return {"message": response["message"], "meta_id": response["meta_id"]}

@router.patch("/metas/{meta_id}", response_model=dict, dependencies=[Depends(auth_middleware)])
async def modificar_meta_ahorro(meta_id: str, meta_data: MetaAhorroBase, request: Request):
    """
    Modificar una meta de ahorro existente.
    """
    usuario_id = request.state.user.id
    response = await financial_controller.modificar_meta_ahorro(usuario_id, meta_id, meta_data)
    return {"message": response["message"]}

@router.delete("/metas/{meta_id}", response_model=dict, dependencies=[Depends(auth_middleware)])
async def eliminar_meta_ahorro(meta_id: str, request: Request):
    """
    Eliminar una meta de ahorro existente.
    """
    usuario_id = request.state.user.id
    response = await financial_controller.eliminar_meta_ahorro(usuario_id, meta_id)
    return {"message": response["message"]}

@router.get("/metas", response_model=List[MetaAhorro], dependencies=[Depends(auth_middleware)])
async def obtener_metas_ahorro(request: Request):
    """
    Obtener todas las metas de ahorro de un usuario.
    """
    usuario_id = request.state.user.id
    metas = await financial_controller.obtener_metas_ahorro(usuario_id)
    return metas

@router.post("/categorias", response_model=dict, status_code=201, dependencies=[Depends(auth_middleware)])
async def crear_categoria_gasto(categoria_data: CategoriaGastoCreate, request: Request):
    """
    Crear una nueva categoría de gasto.
    """
    usuario_id = request.state.user.id
    response = await financial_controller.crear_categoria_gasto(usuario_id, categoria_data)
    return {"message": response["message"]}

@router.get("/categorias", response_model=List[CategoriaGasto], dependencies=[Depends(auth_middleware)])
async def obtener_categorias_gasto(request: Request, periodo: float):
    """
    Obtener las categorías de gasto de un usuario, filtradas por un período de tiempo.
    """
    usuario_id = request.state.user.id
    categorias = await financial_controller.obtener_categorias_gasto(usuario_id, periodo)
    return categorias

@router.post("/gastos", response_model=dict, status_code=201, dependencies=[Depends(auth_middleware)])
async def registrar_gasto(gasto_data: GastoCreate, request: Request):
    """
    Registrar un nuevo gasto.
    """
    usuario_id = request.state.user.id
    response = await financial_controller.registrar_gasto(usuario_id, gasto_data)
    return {"message": response["message"]}

@router.post("/metas/{meta_id}/abono", response_model=dict, dependencies=[Depends(auth_middleware)])
async def abonar_meta(meta_id: str, monto: float, request: Request):
    """
    Abonar a una meta de ahorro específica.
    """
    usuario_id = request.state.user.id
    response = await financial_controller.abonar_meta(usuario_id, meta_id, monto)
    return {"message": response["message"]}