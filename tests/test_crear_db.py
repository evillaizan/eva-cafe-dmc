"""Pruebas de scripts/crear_db.py. Usan una base temporal para no tocar data/cafe.db."""
import sqlite3
from contextlib import closing

from scripts.crear_db import crear

FILAS_ESPERADAS = {
    "categorias": 3,
    "productos": 8,
    "clientes": 3,
    "pedidos": 4,
    "detalle_pedido": 6,
}


def _contar(db, tabla):
    # `tabla` viene de FILAS_ESPERADAS (constante), no de una entrada externa.
    with closing(sqlite3.connect(db)) as con:
        return con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]


def _tablas(db):
    with closing(sqlite3.connect(db)) as con:
        filas = con.execute(
            "SELECT name FROM sqlite_master WHERE type = ? AND name NOT LIKE ?",
            ("table", "sqlite_%"),
        ).fetchall()
    return {nombre for (nombre,) in filas}


def test_crea_todas_las_tablas(tmp_path):
    db = crear(tmp_path / "cafe.db")

    assert _tablas(db) == set(FILAS_ESPERADAS)


def test_carga_datos_de_prueba(tmp_path):
    db = crear(tmp_path / "cafe.db")

    for tabla, esperadas in FILAS_ESPERADAS.items():
        assert _contar(db, tabla) == esperadas, tabla


def test_no_duplica_datos_si_ya_existe(tmp_path):
    db = crear(tmp_path / "cafe.db")

    crear(db)

    assert _contar(db, "productos") == 8


def test_reset_vuelve_al_estado_inicial(tmp_path):
    db = crear(tmp_path / "cafe.db")
    with closing(sqlite3.connect(db)) as con, con:
        con.execute("INSERT INTO categorias (nombre) VALUES (?)", ("Temporal",))

    crear(db, reset=True)

    assert _contar(db, "categorias") == 3
