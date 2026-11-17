# AGENTS.md

## Qué es el sistema

CaféDMC es un sistema de pedidos para una cafetería.
Incluye una API FastAPI, una pantalla Streamlit y una base de datos SQLite.

## Comandos

- Instalar dependencias: `poetry install`
- Ejecutar pruebas: `poetry run pytest -q`
- Revisar estilo: `poetry run ruff check .`

## Arquitectura

- `app/`: código de la API FastAPI y la pantalla Streamlit.
- `tests/`: pruebas automatizadas.
- `scripts/`: scripts auxiliares del proyecto.
- `db/`: base de datos SQLite y recursos relacionados.
- `docs/adr/`: decisiones de arquitectura.

## Reglas

- Gestionar dependencias únicamente con `poetry add`.
- Usar SQL parametrizado.
- Cada endpoint debe tener al menos una prueba.
- No leer archivos `.env`.
- No leer datos de `data/`.
- Mantener `package-mode = false` en la configuración de Poetry.
