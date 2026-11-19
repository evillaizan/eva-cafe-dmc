"""Pruebas del contexto CLIENTES. Usan una base temporal para no tocar data/cafe.db."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from scripts.crear_db import crear


@pytest.fixture()
def cliente(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("CAFE_DB", str(db))
    crear(db)
    return TestClient(app)


def test_listar_clientes(cliente):
    r = cliente.get("/clientes")
    assert r.status_code == 200
    datos = r.json()
    assert [c["email"] for c in datos] == [
        "ana@ejemplo.com", "luis@ejemplo.com", "maria@ejemplo.com"]
    assert set(datos[0]) == {"id", "nombre", "email"}


def test_obtener_cliente(cliente):
    r = cliente.get("/clientes/1")
    assert r.status_code == 200
    assert r.json() == {"id": 1, "nombre": "Ana Torres", "email": "ana@ejemplo.com"}


def test_cliente_inexistente(cliente):
    r = cliente.get("/clientes/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Cliente no encontrado"}
