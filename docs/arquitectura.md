# Arquitectura de CaféDMC

Diagramas C4 de los niveles de contexto, contenedores y componentes. El stack
está en [ADR 0001](adr/0001-stack.md) y el estilo de arquitectura en
[ADR 0002](adr/0002-estilo-arquitectura.md).

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
```

## 3. Componentes de la API

Cómo está organizada por dentro la API FastAPI. Sigue el monolito modular
del [ADR 0002](adr/0002-estilo-arquitectura.md): cada contexto es un módulo
con su router, sus modelos Pydantic, su servicio y su repositorio. Los
endpoints que aparecen son ejemplos.

```mermaid
flowchart TB
    ui["Pantalla Streamlit"]
    db[("SQLite<br/>db/cafe.db")]

    subgraph api["API FastAPI"]
        main["main.py<br/>Crea la app y registra los routers"]
        conexion["db.py<br/>Abre la conexión SQLite"]

        subgraph mod_catalogo["Módulo catalogo"]
            cat_router["router.py<br/>GET /items"]
            cat_schemas["schemas.py<br/>Modelos Pydantic de Item"]
            cat_servicio["servicio.py<br/>Reglas de Item y Stock"]
            cat_repo["repositorio.py<br/>SQL de items y stock"]
        end

        subgraph mod_pedidos["Módulo pedidos"]
            ped_router["router.py<br/>POST /pedidos<br/>PATCH /pedidos/{id}/estado"]
            ped_schemas["schemas.py<br/>Modelos Pydantic de Pedido"]
            ped_servicio["servicio.py<br/>Reglas de Pedido y Estado del Pedido"]
            ped_repo["repositorio.py<br/>SQL de pedidos"]
        end
    end

    ui -- "HTTP/JSON" --> main
    main -- "Registra" --> cat_router
    main -- "Registra" --> ped_router

    cat_router -- "Valida entrada y salida con" --> cat_schemas
    cat_router -- "Llama" --> cat_servicio
    cat_servicio -- "Lee y escribe con" --> cat_repo

    ped_router -- "Valida entrada y salida con" --> ped_schemas
    ped_router -- "Llama" --> ped_servicio
    ped_servicio -- "Lee y escribe con" --> ped_repo
    ped_servicio -- "Consulta precio y reserva stock" --> cat_servicio

    cat_repo -- "Usa" --> conexion
    ped_repo -- "Usa" --> conexion
    conexion -- "SQL parametrizado" --> db
```

Responsabilidad de cada componente:

| Componente | Responsabilidad | No debe |
|---|---|---|
| `main.py` | Crear la app FastAPI y registrar el router de cada módulo. | Contener lógica de negocio. |
| `router.py` | Definir los endpoints, recibir y devolver modelos Pydantic, traducir errores a códigos HTTP. | Ejecutar SQL ni decidir reglas de negocio. |
| `schemas.py` | Definir los modelos Pydantic de entrada y salida del módulo. | Acceder a la base de datos. |
| `servicio.py` | Aplicar las reglas de negocio, como las transiciones de estado del pedido (pendiente, pagado, entregado, anulado) o la validación de stock. Es la única puerta de entrada al módulo para los demás módulos. | Escribir SQL directamente. |
| `repositorio.py` | Leer y escribir las tablas del módulo con SQL parametrizado. | Tocar tablas de otro módulo. |
| `db.py` | Abrir la conexión a SQLite y entregarla a los repositorios (por ejemplo, como dependencia de FastAPI). | Conocer las tablas de los módulos. |

Reglas que muestra el diagrama:

- Las llamadas van en un solo sentido: router → servicio → repositorio →
  SQLite.
- Pedidos usa Catálogo solo a través de `catalogo/servicio.py`, nunca a través
  de su repositorio ni de sus tablas.
- Catálogo no depende de Pedidos.
