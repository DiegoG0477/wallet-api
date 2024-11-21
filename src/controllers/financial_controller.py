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
)
from src.db.mongodb.config import mongo_connection

async def crear_meta_ahorro(usuario_id: str, meta_data: MetaAhorroCreate):
    meta_data_dict = meta_data.model_dump()
    meta_data_dict['usuario_id'] = usuario_id
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    result = await db.insert_one(meta_data_dict)
    return {"message": "Meta de ahorro creada", "meta_id": str(result.inserted_id)}

async def modificar_meta_ahorro(usuario_id: str, meta_id: str, meta_data: MetaAhorroBase):
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    result = await db.update_one(
        {"_id": meta_id, "usuario_id": usuario_id},
        {"$set": meta_data.model_dump()}  # Actualiza los datos de la meta
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
    return {"message": "Meta de ahorro actualizada"}

async def eliminar_meta_ahorro(usuario_id: str, meta_id: str):
    db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    result = await db.delete_one({"_id": meta_id, "usuario_id": usuario_id})
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
    metas_db: AsyncIOMotorCollection = mongo_connection.database["metas_ahorro"]
    ingresos_db: AsyncIOMotorCollection = mongo_connection.database["ingresos"]
    
    result = await metas_db.update_one(
        {"_id": meta_id, "usuario_id": usuario_id},
        {"$inc": {"monto_actual": monto}}  # Incrementa el monto de la meta
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")

    ingreso = {
        "usuario_id": usuario_id,
        "monto": monto,
        "fecha": datetime.now(),
        "descripcion": f"Abono a la meta {meta_id}"
    }
    
    await ingresos_db.insert_one(ingreso)  # Registra el abono como ingreso
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
