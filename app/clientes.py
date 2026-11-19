"""Contexto CLIENTES: consulta de clientes. Solo lee su propia tabla."""
from fastapi import APIRouter, HTTPException

from app.db import Conexion
from app.modelos import Cliente, PedidoHistorial
from app.pedidos import pedidos_de_cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])

SQL_BASE = "SELECT id, nombre, email FROM clientes"


@router.get("", response_model=list[Cliente])
def listar_clientes(con: Conexion):
    filas = con.execute(SQL_BASE + " ORDER BY id").fetchall()
    return [dict(f) for f in filas]


@router.get("/{cliente_id}", response_model=Cliente)
def obtener_cliente(cliente_id: int, con: Conexion):
    fila = con.execute(SQL_BASE + " WHERE id = ?", (cliente_id,)).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return dict(fila)


@router.get("/{cliente_id}/pedidos", response_model=list[PedidoHistorial])
def historial_de_pedidos(cliente_id: int, con: Conexion):
    if con.execute(SQL_BASE + " WHERE id = ?", (cliente_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return pedidos_de_cliente(con, cliente_id)
