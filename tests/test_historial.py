"""Pruebas de GET /clientes/{id}/pedidos. Usan una base temporal para no tocar data/cafe.db."""
import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

from app.main import app
from scripts.crear_db import crear


@pytest.fixture()
def db(tmp_path, monkeypatch):
    ruta = tmp_path / "test.db"
    monkeypatch.setenv("CAFE_DB", str(ruta))
    crear(ruta)
    return ruta


@pytest.fixture()
def cliente(db):
    return TestClient(app)


def test_historial_de_cliente(cliente):
    # Semilla: Ana (id 1) tiene los pedidos 1 y 4, ambos entregados
    r = cliente.get("/clientes/1/pedidos")
    assert r.status_code == 200
    pedidos = r.json()
    assert {p["id"] for p in pedidos} == {1, 4}
    assert all(p["cliente_id"] == 1 for p in pedidos)
    assert set(pedidos[0]) == {"id", "cliente_id", "estado", "total", "fecha"}


def test_historial_mas_reciente_primero(cliente):
    nuevo = cliente.post("/pedidos", json={"cliente_id": 1, "items": [
        {"producto_id": 1, "cantidad": 1}]}).json()
    pedidos = cliente.get("/clientes/1/pedidos").json()
    assert pedidos[0]["id"] == nuevo["id"]
    assert pedidos[0]["estado"] == "pendiente"
    assert len(pedidos) == 3


def test_historial_no_mezcla_clientes(cliente):
    pedidos = cliente.get("/clientes/2/pedidos").json()
    assert [p["id"] for p in pedidos] == [2]


def test_cliente_sin_pedidos(cliente, db):
    with closing(sqlite3.connect(db)) as con, con:
        con.execute("INSERT INTO clientes (nombre, email) VALUES (?, ?)",
                    ("Sin Pedidos", "sin@ejemplo.com"))
    r = cliente.get("/clientes/4/pedidos")
    assert r.status_code == 200
    assert r.json() == []


def test_historial_cliente_inexistente(cliente):
    r = cliente.get("/clientes/999/pedidos")
    assert r.status_code == 404
    assert r.json() == {"detail": "Cliente no encontrado"}
