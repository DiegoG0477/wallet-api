from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.db.postgresql.config import Base
from datetime import date

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String(150), primary_key=True)
    correo = Column(String(150), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    fecha_registro = Column(Date, nullable=False, default=date.today)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True)
    pais_id = Column(Integer, ForeignKey("paises.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados.id"), nullable=False)
    direccion = Column(String(255), nullable=True)
    
    pais = relationship("Pais", back_populates="usuarios")
    estado = relationship("Estado", back_populates="usuarios")

class Pais(Base):
    __tablename__ = "paises"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)

    usuarios = relationship("Usuario", back_populates="pais")
    estados = relationship("Estado", back_populates="pais")

class Estado(Base):
    __tablename__ = "estados"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    pais_id = Column(Integer, ForeignKey("paises.id"), nullable=False)
    
    pais = relationship("Pais", back_populates="estados")
    usuarios = relationship("Usuario", back_populates="estado")
