# Arquitectura de CaféDMC

Diagramas C4 de los niveles de contexto y contenedores. El stack está en
[ADR 0001](adr/0001-stack.md).

## 1. Contexto

Quién usa el sistema.

```mermaid
flowchart LR
    cliente["👤 Cliente<br/>de la cafetería"]
    dev["👤 Desarrollador"]
    agente["🤖 Agente IA"]
    sistema["CaféDMC<br/>Sistema de pedidos"]

    cliente -- "Ve el menú y pide" --> sistema
    dev -- "Desarrolla y prueba" --> sistema
    dev -- "Da tareas" --> agente
    agente -- "Lee, prueba y modifica" --> sistema
```

## 2. Contenedores

Las piezas que se ejecutan dentro de CaféDMC.

```mermaid
flowchart LR
    cliente["👤 Cliente"]
    agente["🤖 Agente IA"]

    subgraph cafedmc["CaféDMC"]
        ui["Pantalla<br/>Streamlit"]
        subgraph api["API FastAPI"]
            catalogo["Catálogo"]
            pedidos["Pedidos"]
        end
        mcp["Servidores MCP"]
        db[("SQLite")]
    end

    cliente -- "Usa" --> ui
    ui -- "HTTP/JSON" --> api
    catalogo -- "SQL" --> db
    pedidos -- "SQL" --> db

    agente -- "Consulta" --> mcp
    mcp -- "Solo lectura" --> db
    agente -- "Escrituras<br/>HTTP/JSON" --> api
```

Reglas que muestra el diagrama:

- Solo la API escribe en SQLite.
- El agente lee los datos a través de MCP en modo solo lectura. Para cambiar
  datos, usa la API, que aplica las reglas de negocio.

```mermaid
flowchart LR
  ui[Pantalla Streamlit] -->|HTTP JSON| api[API FastAPI]
  api --> cat[Contexto catálogo]
  api --> ped[Contexto pedidos]
  cat --> db[(SQLite cafe.db)]
  ped --> db
  agente[Agente IA] -->|MCP| mcp[Servidores MCP]
  mcp -->|solo lectura| db
  mcp -->|escrituras| api