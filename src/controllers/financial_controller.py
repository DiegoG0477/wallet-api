from fastapi import HTTPException
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from src.models.financial_models import (
    GastoModel,
    CategoriaGastoModel,
    MetaAhorroModel
)
from src.schemas.financial_schemas import (
    MetaAhorroBase,
    MetaAhorro,
    MetaAhorroCreate,
    CategoriaGastoCreate,
    CategoriaGastoGet,
    GastoGet,
    Ingreso,
    IngresoCreate,
    UsuarioFinanciero
)
from bson import ObjectId
from src.db.mongodb.config import mongo_connection
from typing import Optional

async def crear_meta_ahorro(usuario_id: str, meta_data: MetaAhorroCreate):
    meta_data_dict = meta_data.model_dump()
    meta_data_dict['usuario_id'] = usuario_id

    meta_document = MetaAhorroModel(
        usuario_id=usuario_id,
        nombre=meta_data.nombre,
        monto_objetivo=meta_data.monto_objetivo,
        fecha_inicio=meta_data.fecha_inicio,
        fecha_objetivo=meta_data.fecha_objetivo
    )

    meta_data_dict = meta_document.model_dump(by_alias=True)

    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    result = await db.insert_one(meta_data_dict)
    return {"message": "Meta de ahorro creada", "meta_id": str(result.inserted_id)}

async def modificar_meta_ahorro(usuario_id: str, meta_id: str, meta_data: MetaAhorroBase):
    """
    Modificar una meta de ahorro.
    """
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]

    try:
        object_id = ObjectId(meta_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de meta inválido")

    result = await db.update_one(
        {"_id": object_id, "usuario_id": usuario_id},
        {"$set": meta_data.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")

    return {"message": "Meta de ahorro actualizada"}


async def eliminar_meta_ahorro(usuario_id: str, meta_id: str):
    """
    Eliminar una meta de ahorro.
    """
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]

    try:
        object_id = ObjectId(meta_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de meta inválido")

    result = await db.delete_one({"_id": object_id, "usuario_id": usuario_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")

    return {"message": "Meta de ahorro eliminada"}

async def crear_categoria_gasto(usuario_id: str, categoria_data: CategoriaGastoCreate):
    db: AsyncIOMotorCollection = mongo_connection.database["categorias_gasto"]

    categoria_document = CategoriaGastoModel(
        usuario_id=usuario_id,
        nombre=categoria_data.nombre,
        limite_gasto=categoria_data.limite_gasto,
    )

    categoria_data_dict = categoria_document.model_dump(by_alias=True)
    result = await db.insert_one(categoria_data_dict)
    return {"message": "Categoría de gasto creada", "categoria_id": str(result.inserted_id)}

async def abonar_meta(usuario_id: str, meta_id: str, monto: float):
    """
    Abonar a una meta de ahorro y registrar el ingreso.
    """
    metas_db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    ingresos_db: AsyncIOMotorCollection = mongo_connection.database["ingresos"]
    
    try:
        object_id = ObjectId(meta_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de meta inválido")

    result = await metas_db.update_one(
        {"_id": object_id, "usuario_id": usuario_id},
        {"$inc": {"monto_actual": monto}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")

    ingreso = {
        "usuario_id": usuario_id,
        "monto": monto,
        "fecha": datetime.now(),
        "descripcion": f"Abono a la meta {meta_id}",
        "meta_id": meta_id
    }

    await ingresos_db.insert_one(ingreso)

    return {"message": "Abono realizado y registrado como ingreso"}

async def registrar_gasto(usuario_id: str, gasto_data: GastoModel):
    gastos_db: AsyncIOMotorCollection = mongo_connection.database["gastos"]
    categorias_db: AsyncIOMotorCollection = mongo_connection.database["categorias_gasto"]

    try:
        object_id = ObjectId(gasto_data.categoria_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de categoría inválido")

    result = await categorias_db.update_one(
        {"_id": object_id, "usuario_id": usuario_id},
        {"$inc": {"gasto_total": gasto_data.monto}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Categoría de gasto no encontrada")

    gasto_data_dict = gasto_data.model_dump()  # Convierte los datos del modelo a diccionario
    gasto_data_dict['usuario_id'] = usuario_id  # Asigna el usuario_id al gasto
    result = await gastos_db.insert_one(gasto_data_dict)  # Inserta el gasto en la base de datos

    return {"message": "Gasto registrado", "gasto_id": str(result.inserted_id)}

async def obtener_metas_ahorro(usuario_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    metas_cursor = db.find({"usuario_id": usuario_id})
    metas = await metas_cursor.to_list(length=None)
    for meta in metas:
        meta["_id"] = str(meta["_id"])
    metas_parsed = [MetaAhorro(**meta) for meta in metas]
    return metas_parsed

async def obtener_categorias_gasto(usuario_id: str, periodo: float):
    categorias_db: AsyncIOMotorCollection = mongo_connection.database["categorias_gasto"]
    gastos_db: AsyncIOMotorCollection = mongo_connection.database["gastos"]

    now = datetime.now()
    if periodo >= 1:
        start_date = now - timedelta(days=(30 * periodo))
    elif periodo == 0.5:
        start_date = now - timedelta(days=14)
    elif periodo == 0.25:
        start_date = now - timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail="Período no válido")

    categorias_cursor = categorias_db.find({"usuario_id": usuario_id, "deleted": 0})
    categorias = await categorias_cursor.to_list(length=None)

    categorias_parsed = []
    for categoria in categorias:
        categoria["_id"] = str(categoria["_id"])
        gastos_cursor = gastos_db.find(
            {
                "usuario_id": usuario_id,
                "categoria_id": categoria["_id"],
                "fecha": {"$gte": start_date, "$lte": (now + timedelta(days=1))},
            }
        )
        gastos = await gastos_cursor.to_list(length=None)
        total_gastado = sum(gasto["monto"] for gasto in gastos)
        categoria["gasto_actual"] = total_gastado

        categorias_parsed.append(CategoriaGastoGet(**categoria))

    return categorias_parsed

async def obtener_gastos(usuario_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["gastos"]
    gastos_cursor = db.find({"usuario_id": usuario_id})
    gastos = await gastos_cursor.to_list(length=None)
    gastos_parsed = []

    for gasto in gastos:
        gasto["_id"] = str(gasto["_id"])

        gastos_parsed.append(GastoGet(**gasto))

    return gastos_parsed


async def obtener_ingresos(usuario_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["ingresos"]
    ingresos_cursor = db.find({"usuario_id": usuario_id})
    ingresos = await ingresos_cursor.to_list(length=None)
    for ingreso in ingresos:
        ingreso["_id"] = str(ingreso["_id"])
    ingresos_parsed = [Ingreso(**ingreso) for ingreso in ingresos]
    return ingresos_parsed


async def registrar_ingreso(usuario_id: str, ingreso_data: IngresoCreate):
    ingreso_data_dict = ingreso_data.model_dump()
    ingreso_data_dict['usuario_id'] = usuario_id
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    result = await db.insert_one(ingreso_data_dict)
    return {"message": "Ingreso registrado", "ingreso_id": str(result.inserted_id)}

async def obtener_datos_financieros(usuario_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["usuarios_financieros"]
    datos_cursor = db.find({"usuario_id": usuario_id})
    datos = await datos_cursor.to_list(length=None)

    for dato in datos:
        dato["_id"] = str(dato["_id"])

    datos_parsed = [UsuarioFinanciero(**dato) for dato in datos]
    return datos_parsed

async def obtener_meta_by_id(meta_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]

    try:
        object_id = ObjectId(meta_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de meta inválido")

    meta = await db.find_one({"_id": object_id})
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta no encontrada")

    meta["_id"] = str(meta["_id"])

    meta_parsed = MetaAhorro(**meta)
    return meta_parsed

async def obtener_abonos_by_meta_id(meta_id: str, limit: Optional[int] = None):
    db: AsyncIOMotorCollection = mongo_connection.database["ingresos"]

    ingresos_cursor = db.find({"meta_id": meta_id})
    if limit:
        ingresos_cursor = ingresos_cursor.limit(limit)
    
    ingresos = await ingresos_cursor.to_list(length=None)

    for ingreso in ingresos:
        ingreso["_id"] = str(ingreso["_id"])
    ingresos_parsed = [Ingreso(**ingreso) for ingreso in ingresos]
    return ingresos_parsed

async def get_resumen(usuario_id: str, periodo: int):
    categorias_db: AsyncIOMotorCollection = mongo_connection.database["categorias_gasto"]
    gastos_db: AsyncIOMotorCollection = mongo_connection.database["gastos"]

    now = datetime.now()
    if periodo >= 1:
        start_date = now - timedelta(days=(30 * periodo))
    elif periodo == 0.5:
        start_date = now - timedelta(days=14)
    elif periodo == 0.25:
        start_date = now - timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail="Período no válido")

    categorias_cursor = categorias_db.find({"usuario_id": usuario_id, "deleted": 0})
    categorias = await categorias_cursor.to_list(length=None)   

    resumen = {}

    total_gastado = 0
    limite_total = 0
    for categoria in categorias:
        categoria["_id"] = str(categoria["_id"])
        gastos_cursor = gastos_db.find(
            {
                "usuario_id": usuario_id,
                "categoria_id": categoria["_id"],
                "fecha": {"$gte": start_date, "$lte": (now + timedelta(days=1))},
            }
        )
        gastos = await gastos_cursor.to_list(length=None)
        total_gastado += sum(gasto["monto"] for gasto in gastos) or 0
        limite_total += categoria["limite_gasto"]
        
    resumen["gasto_total"] = total_gastado
    resumen["limite_total"] = limite_total
    resumen["balance"] = limite_total - total_gastado

    return resumen

async def eliminar_categoria(usuario_id: str, categoria_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["categorias_gasto"]
    try:
        object_id = ObjectId(categoria_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de categoría inválido")

    categoria = await db.find_one({"_id": object_id, "usuario_id": usuario_id})
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    result = await db.update_one({"_id": object_id}, {"$set": {"deleted": 1}})
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="No se pudo eliminar la categoría")

    return {"message": "Categoría eliminada correctamente"}