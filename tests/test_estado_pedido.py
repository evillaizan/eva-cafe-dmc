"""Pruebas del cambio de estado del pedido. Usan una base temporal para no tocar data/cafe.db."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from scripts.crear_db import crear

# Camino de transiciones permitidas para llevar un pedido nuevo (pendiente) a cada estado
CAMINOS = {
    "pendiente": [],
    "pagado": ["pagado"],
    "entregado": ["pagado", "entregado"],
    "anulado": ["anulado"],
}


@pytest.fixture()
def cliente(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("CAFE_DB", str(db))
    crear(db)
    return TestClient(app)


def crear_pedido(cliente) -> int:
    """Crea un pedido nuevo (queda en 'pendiente') y devuelve su id."""
    r = cliente.post("/pedidos", json={"cliente_id": 1, "items": [
        {"producto_id": 1, "cantidad": 1}]})
    assert r.status_code == 201
    return r.json()["id"]


def cambiar_estado(cliente, pedido_id: int, estado: str):
    return cliente.patch(f"/pedidos/{pedido_id}/estado", json={"estado": estado})


def pedido_en_estado(cliente, estado: str) -> int:
    """Crea un pedido y lo lleva a `estado` usando solo transiciones permitidas."""
    pedido_id = crear_pedido(cliente)
    for paso in CAMINOS[estado]:
        assert cambiar_estado(cliente, pedido_id, paso).status_code == 200
    assert cliente.get(f"/pedidos/{pedido_id}").json()["estado"] == estado
    return pedido_id


@pytest.mark.parametrize("desde, hacia", [
    ("pendiente", "pagado"),
    ("pagado", "entregado"),
    ("pendiente", "anulado"),
    ("pagado", "anulado"),
])
def test_transicion_permitida(cliente, desde, hacia):
    pedido_id = pedido_en_estado(cliente, desde)
    r = cambiar_estado(cliente, pedido_id, hacia)
    assert r.status_code == 200
    datos = r.json()
    assert datos["id"] == pedido_id
    assert datos["cliente_id"] == 1
    assert datos["estado"] == hacia
    assert datos["total"] == 7.0
    assert cliente.get(f"/pedidos/{pedido_id}").json()["estado"] == hacia


def test_transicion_permitida_pedido_semilla(cliente):
    # Pedido 2 de la semilla está 'pagado'
    r = cambiar_estado(cliente, 2, "entregado")
    assert r.status_code == 200
    assert cliente.get("/pedidos/2").json()["estado"] == "entregado"


@pytest.mark.parametrize("desde, hacia", [
    ("pendiente", "entregado"),
    ("pagado", "pendiente"),
    ("entregado", "anulado"),
    ("entregado", "pagado"),
    ("anulado", "pagado"),
    ("pendiente", "pendiente"),
    ("pagado", "pagado"),
])
def test_transicion_no_permitida(cliente, desde, hacia):
    pedido_id = pedido_en_estado(cliente, desde)
    r = cambiar_estado(cliente, pedido_id, hacia)
    assert r.status_code == 409
    assert r.json() == {"detail": f"Transición no permitida: {desde} → {hacia}"}
    assert cliente.get(f"/pedidos/{pedido_id}").json()["estado"] == desde


def test_pedido_inexistente(cliente):
    r = cambiar_estado(cliente, 999, "pagado")
    assert r.status_code == 404
    assert r.json() == {"detail": "Pedido no encontrado"}


def test_estado_desconocido(cliente):
    pedido_id = crear_pedido(cliente)
    r = cambiar_estado(cliente, pedido_id, "cancelado")
    assert r.status_code == 422
    assert cliente.get(f"/pedidos/{pedido_id}").json()["estado"] == "pendiente"
