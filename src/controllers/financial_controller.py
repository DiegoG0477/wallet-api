from fastapi import HTTPException
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from src.models.financial_models import (
    GastoModel,
)
from src.schemas.financial_schemas import (
    MetaAhorroBase,
    MetaAhorro,
    MetaAhorroCreate,
    CategoriaGastoCreate,
    CategoriaGastoGet,
    Gasto,
    Ingreso,
    IngresoCreate,
    UsuarioFinanciero
)
from bson import ObjectId
from src.db.mongodb.config import mongo_connection

async def crear_meta_ahorro(usuario_id: str, meta_data: MetaAhorroCreate):
    meta_data_dict = meta_data.model_dump()
    meta_data_dict['usuario_id'] = usuario_id
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    result = await db.insert_one(meta_data_dict)
    return {"message": "Meta de ahorro creada", "meta_id": str(result.inserted_id)}

async def modificar_meta_ahorro(usuario_id: str, meta_id: str, meta_data: MetaAhorroBase):
    """
    Modificar una meta de ahorro.
    """
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]

    # Convertir meta_id a ObjectId
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
    categoria_data_dict = categoria_data.model_dump()  # Convierte los datos del modelo a diccionario
    categoria_data_dict['usuario_id'] = usuario_id  # Asigna el usuario_id a la categoría
    result = await db.insert_one(categoria_data_dict)  # Inserta la categoría de gasto
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
        "descripcion": f"Abono a la meta {meta_id}"
    }

    await ingresos_db.insert_one(ingreso)

    return {"message": "Abono realizado y registrado como ingreso"}


async def registrar_gasto(usuario_id: str, gasto_data: GastoModel):
    gastos_db: AsyncIOMotorCollection = mongo_connection.database["gastos"]
    gasto_data_dict = gasto_data.model_dump()  # Convierte los datos del modelo a diccionario
    gasto_data_dict['usuario_id'] = usuario_id  # Asigna el usuario_id al gasto
    result = await gastos_db.insert_one(gasto_data_dict)  # Inserta el gasto en la base de datos
    return {"message": "Gasto registrado", "gasto_id": str(result.inserted_id)}


async def obtener_metas_ahorro(usuario_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    metas_cursor = db.find({"usuario_id": usuario_id})  # Busca las metas de ahorro del usuario
    metas = await metas_cursor.to_list(length=None)  # Convierte el cursor a lista
    for meta in metas:
        meta["_id"] = str(meta["_id"])
    metas_parsed = [MetaAhorro(**meta) for meta in metas]  # Convierte a modelo MetaAhorro
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

    categorias_cursor = categorias_db.find({"$or": [
        {"usuario_id": usuario_id}, 
        {"usuario_id": "async default"}
    ]})
    categorias = await categorias_cursor.to_list(length=None)

    categorias_parsed = []
    for categoria in categorias:
        categoria["_id"] = str(categoria["_id"])
        gastos_cursor = gastos_db.find(
            {
                "usuario_id": usuario_id,
                "categoria_id": categoria["_id"],
                "fecha": {"$gte": start_date, "$lte": now},
            }
        )
        gastos = await gastos_cursor.to_list(length=None)
        total_gastado = sum(gasto["monto"] for gasto in gastos)
        categoria["total_gastado"] = total_gastado
        categorias_parsed.append(CategoriaGastoGet(**categoria))

    return categorias_parsed

async def obtener_gastos(usuario_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["gastos"]
    gastos_cursor = db.find({"usuario_id": usuario_id})
    gastos = await gastos_cursor.to_list(length=None)
    for gasto in gastos:
        gasto["_id"] = str(gasto["_id"])
    gastos_parsed = [Gasto(**gasto) for gasto in gastos]
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
    for dato in datos_cursor:
        dato["_id"] = str(dato["_id"])
    datos_parsed = [UsuarioFinanciero(**dato) for dato in datos]
    return datos_parsed