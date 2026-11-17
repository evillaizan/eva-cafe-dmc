# ADR 0001: Stack tecnológico de CaféDMC

## Estado

Propuesto

## Fecha

2026-11-16

## Contexto

- El equipo sabe Python.
- Cada alumno ejecuta el sistema en su laptop, sin Docker.
- Los agentes de IA deben poder leer, probar y modificar el sistema sin
  configuración extra.

## Decisión

Usar:

- **Python 3.11+** como lenguaje.
- **Poetry** para dependencias y entorno virtual (`package-mode = false`).
- **FastAPI + Pydantic** para la API y la validación de datos.
- **SQLite** como base de datos (un archivo en `db/`).
- **Streamlit** para la pantalla de usuario.
- **pytest** para las pruebas y **ruff** para el estilo.

## Consecuencias

**Positivas (+)**

- Todo corre con `poetry install`; no hace falta instalar servicios aparte.
- SQLite viene incluido en Python: no hay servidor que levantar ni credenciales.
- FastAPI y Pydantic tipan las entradas y salidas, y generan documentación
  OpenAPI. Eso hace el código explícito y fácil de leer para personas y agentes.
- `TestClient` de FastAPI y pytest permiten probar cada endpoint sin levantar
  el servidor.
- Comandos únicos y conocidos (`poetry run pytest -q`, `poetry run ruff check .`)
  que un agente puede ejecutar para verificar sus cambios.

**Negativas (−)**

- SQLite soporta mal la escritura concurrente y no es adecuado para producción
  con muchos usuarios.
- FastAPI no trae ORM, migraciones, autenticación ni panel de administración;
  si hacen falta, hay que agregarlos.
- Streamlit sirve para prototipos, pero limita el diseño y el control de la
  interfaz.
- Hay dos procesos (API y Streamlit) que ejecutar por separado.

## Alternativas consideradas

| Alternativa | Por qué no |
|---|---|
| **Django** (en lugar de FastAPI + Streamlit) | Trae ORM, admin y autenticación, pero es más pesado y tiene más convenciones implícitas ("magia") que un agente debe conocer. Para una API pequeña sobra. |
| **PostgreSQL** (en lugar de SQLite) | Mejor concurrencia y más cercano a producción, pero exige instalar y configurar un servidor en cada laptop o usar Docker, lo que el contexto descarta. Se puede migrar después si el sistema crece. |
| **Flask** (en lugar de FastAPI) | Simple, pero sin validación ni tipado de entradas integrado; habría que sumar librerías. |
| **pip + venv** (en lugar de Poetry) | Sin archivo de bloqueo (`poetry.lock`); las versiones pueden variar entre laptops. |
