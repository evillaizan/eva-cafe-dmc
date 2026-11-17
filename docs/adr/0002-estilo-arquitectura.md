# ADR 0002: Estilo de arquitectura de CaféDMC

## Estado

Propuesto

## Fecha

2026-11-16

## Contexto

- CaféDMC es un sistema de pedidos para una cafetería, con pocos usuarios
  simultáneos.
- El dominio tiene contextos distinguibles (ver glosario en `AGENTS.md`):
  **Pedidos** (`Pedido`, `Estado del Pedido`), **Catálogo** (`Item`, `Stock`)
  y **Clientes** (`Cliente`).
- Esos contextos colaboran mucho: crear un pedido consulta el catálogo,
  descuenta stock y referencia a un cliente, idealmente en una sola
  transacción.
- Según el ADR 0001, el sistema corre en la laptop de cada alumno, sin Docker,
  con SQLite y `poetry install` como única instalación.
- Lo construye un equipo pequeño que despliega todo junto.
- Los agentes de IA deben poder entender, probar y modificar el sistema
  completo con los comandos de `AGENTS.md`.

## Decisión

CaféDMC empieza como **monolito modular**: un solo proceso FastAPI, con el
código separado en módulos por contexto.

```
app/
  pedidos/     # router, servicio, repositorio y modelos de Pedido
  catalogo/    # Item y Stock
  clientes/    # Cliente
  main.py      # crea la app FastAPI y registra los routers de cada módulo
  ui/          # pantalla Streamlit (cliente de la API)
```

Reglas para que los módulos sigan separados:

1. Cada módulo es dueño de sus tablas. Solo su repositorio las lee o escribe
   con SQL.
2. Un módulo usa a otro únicamente a través de las funciones públicas de su
   servicio (por ejemplo, `catalogo.servicio.reservar_stock(...)`), nunca
   importando su repositorio ni consultando sus tablas.
3. No se permiten dependencias circulares entre módulos. La dirección
   esperada es `pedidos → catalogo` y `pedidos → clientes`.
4. Cada módulo tiene sus propias pruebas en `tests/<modulo>/`.

## Consecuencias

**Positivas (+)**

- Un solo proceso y una sola base SQLite: se mantiene el arranque simple del
  ADR 0001.
- Crear un pedido y descontar stock ocurre en una transacción local, sin
  coordinar sistemas distribuidos (sagas, reintentos, mensajes).
- Llamar a otro módulo es una llamada a una función, sin latencia de red ni
  fallas parciales.
- `poetry run pytest -q` prueba todo el sistema de una vez. Un agente ve el
  código completo en un solo repositorio y puede rastrear un flujo de punta a
  punta.
- Los límites por contexto dejan preparada una futura extracción a servicios
  si llegara a hacer falta.

**Negativas (−)**

- Los límites entre módulos dependen de disciplina y de revisión: Python no
  impide que un módulo importe el repositorio de otro. Se puede mitigar con
  una prueba que revise los imports o con una herramienta como
  `import-linter`.
- Todo se despliega y escala junto: un error grave en un módulo tumba el
  proceso entero.
- Compartir la base facilita romper la regla 1 "por atajo" con un `JOIN`
  entre tablas de distintos módulos.

## Alternativas consideradas

| Alternativa | Por qué no |
|---|---|
| **Microservicios** (un proceso y una base por contexto) | Obligaría a levantar tres o más procesos en cada laptop, a comunicarlos por HTTP o mensajes y a coordinar la consistencia entre pedido y stock sin transacción común. Agrega complejidad operativa que un equipo pequeño y un sistema de bajo tráfico no necesitan, y va contra el "sin Docker, solo `poetry install`" del ADR 0001. |
| **Monolito sin módulos** (organizado por capa técnica: `routers/`, `models/`, `db/`) | Es igual de simple al arrancar, pero mezcla los contextos: cambiar Pedidos obliga a tocar archivos compartidos con Catálogo, y extraer un servicio después sería mucho más caro. |

## Cuándo cambiaríamos esta decisión

Extraeríamos un módulo como servicio independiente solo si se cumple al menos
una de estas condiciones, y la dificultad no se resuelve dentro del monolito:

- **Escala distinta**: un contexto necesita escalar por separado (por
  ejemplo, Catálogo recibe mucho más tráfico de lectura que Pedidos) y escalar
  el monolito completo ya no es razonable.
- **Equipos independientes**: varios equipos trabajan en contextos distintos y
  coordinar un único despliegue los frena de forma habitual.
- **Disponibilidad distinta**: una caída de un contexto no debe afectar a los
  demás (por ejemplo, que se puedan seguir tomando pedidos aunque falle un
  módulo de reportes o de pagos externos).
- **Tecnología distinta**: un contexto necesita otro lenguaje, runtime o base
  de datos que no conviene meter en el proceso principal.
- **Integración externa**: un tercero (por ejemplo, una pasarela de pago o una
  app de delivery) debe consumir un contexto con su propio ciclo de versiones.

Cosas que **no** justifican pasar a microservicios por sí solas:

- **Problemas de concurrencia de SQLite**: primero se migra a PostgreSQL (ver
  ADR 0001), sin cambiar el estilo de arquitectura.
- **Código desordenado**: se corrige reforzando los límites entre módulos;
  separarlo en servicios solo distribuiría el desorden.
- **Querer "estar preparados"**: las reglas de módulos de esta decisión ya
  dejan el camino abierto sin pagar el costo por adelantado.

Si se cumple un disparador, se extrae **un módulo a la vez**, empezando por el
que tenga menos dependencias entrantes, y se registra en un nuevo ADR que
reemplace a este.
