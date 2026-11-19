"""Contexto CLIENTES: consulta de clientes. Solo lee su propia tabla."""
from fastapi import APIRouter, HTTPException

from app.db import Conexion
from app.modelos import Cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("/{cliente_id}", response_model=Cliente)
def obtener_cliente(cliente_id: int, con: Conexion):
    fila = con.execute("SELECT id, nombre, email FROM clientes WHERE id = ?",
                       (cliente_id,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return dict(fila)
