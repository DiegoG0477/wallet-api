from fastapi import HTTPException
from datetime import datetime, timedelta
from pymongo.collection import Collection
from src.models.financial_models import (
    MetaAhorroModel,
    CategoriaGastoModel,
    GastoModel,
    IngresoModel,
)
from src.schemas.financial_schemas import (
    MetaAhorroBase,
    MetaAhorro,
    MetaAhorroCreate,
    CategoriaGastoCreate,
    CategoriaGastoGet,
)
from src.db.mongodb.config import mongo_connection


class FinancialController:
    @staticmethod
    def crear_meta_ahorro(meta_data: MetaAhorroCreate):
        """
        Crear una nueva meta de ahorro.
        """
        db: Collection = mongo_connection.database["metas_ahorro"]
        meta = db.insert_one(meta_data.model_dump())
        return {"message": "Meta de ahorro creada", "meta_id": str(meta.inserted_id)}

    @staticmethod
    def modificar_meta_ahorro(meta_id: str, meta_data: MetaAhorroBase):
        """
        Modificar una meta de ahorro.
        """
        db: Collection = mongo_connection.database["metas_ahorro"]
        result = db.update_one({"_id": meta_id}, {"$set": meta_data.model_dump()})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
        return {"message": "Meta de ahorro actualizada"}

    @staticmethod
    def eliminar_meta_ahorro(meta_id: str):
        """
        Eliminar una meta de ahorro.
        """
        db: Collection = mongo_connection.database["metas_ahorro"]
        result = db.delete_one({"_id": meta_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
        return {"message": "Meta de ahorro eliminada"}

    @staticmethod
    def crear_categoria_gasto(categoria_data: CategoriaGastoCreate):
        """
        Crear una nueva categoría de gasto.
        """
        db: Collection = mongo_connection.database["categorias_gasto"]
        categoria = db.insert_one(categoria_data.model_dump())
        return {"message": "Categoría de gasto creada", "categoria_id": str(categoria.inserted_id)}

    @staticmethod
    def abonar_meta(usuario_id: str, meta_id: str, monto: float):
        """
        Abonar a una meta de ahorro y registrar el ingreso.
        """
        metas_db: Collection = mongo_connection.database["metas_ahorro"]
        ingresos_db: Collection = mongo_connection.database["ingresos"]

        result = metas_db.update_one(
            {"_id": meta_id, "usuario_id": usuario_id},
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

        ingresos_db.insert_one(ingreso)
        return {"message": "Abono realizado y registrado como ingreso"}

    @staticmethod
    def registrar_gasto(gasto_data: GastoModel):
        """
        Registrar un gasto en la colección de gastos.
        """
        gastos_db: Collection = mongo_connection.database["gastos"]
        gasto = gastos_db.insert_one(gasto_data.model_dump())
        return {"message": "Gasto registrado", "gasto_id": str(gasto.inserted_id)}

    @staticmethod
    def obtener_metas_ahorro(usuario_id: str):
        """
        Obtener las metas de ahorro de un usuario.
        """
        db: Collection = mongo_connection.database["metas_ahorro"]
        metas = list(db.find({"usuario_id": usuario_id}))

        # Convertir los resultados a MetaAhorro usando Pydantic
        metas_parsed = [MetaAhorro(**meta) for meta in metas]
        return metas_parsed

    @staticmethod
    def obtener_categorias_gasto(usuario_id: str, periodo: float):
        """
        Obtener categorías de gasto y calcular el total gastado por categoría.
        """
        categorias_db: Collection = mongo_connection.database["categorias_gasto"]
        gastos_db: Collection = mongo_connection.database["gastos"]

        now = datetime.now()
        if periodo >= 1:  # Mes(es)
            start_date = now - timedelta(days=(30*periodo))
        elif periodo == 0.5:  # Dos semanas
            start_date = now - timedelta(days=14)
        elif periodo == 0.25:  # Una semana
            start_date = now - timedelta(days=7)
        else:
            raise HTTPException(status_code=400, detail="Período no válido")

        categorias = list(categorias_db.find({"$or": [
                {"usuario_id": usuario_id}, 
                {"usuario_id": "default"}
            ]}))

        # Calcular el total gastado por categoría
        categorias_parsed = []
        for categoria in categorias:
            gastos = list(
                gastos_db.find(
                    {
                        "usuario_id": usuario_id,
                        "categoria_id": str(categoria["_id"]),
                        "fecha": {"$gte": start_date, "$lte": now},
                    }
                )
            )
            total_gastado = sum(gasto["monto"] for gasto in gastos)

            # Parsear la categoría con el total gastado
            categoria["total_gastado"] = total_gastado
            categorias_parsed.append(CategoriaGastoGet(**categoria))

        return categorias_parsed