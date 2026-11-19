# Bitácora de evidencias · Edson Villaizan

## Sesión 1 · 16/nov/2026
- Captura: `poetry run python --version` y `poetry env info --path`
- Captura: el agente responde el comando de pruebas
- Captura: diagrama de contenedores renderizado
- Error que tuve y cómo lo resolví:
- Qué corregí de lo que propuso el agente:
- `¿qué versión de pytest quedó instalada?` : `poetry show` lista paquetes; 
- `¿de qué paquetes depende ruff?` : `poetry show --tree` muestra dependencias.
- `¿en qué ruta está tu entorno?` : `poetry env info `


## Sesión 2 · 18/nov/2026 · Códigos HTTP desde `/docs`

Provoqué cada respuesta en Swagger (`http://127.0.0.1:8000/docs` → `POST /pedidos` → *Try it out* → *Execute*).
Capturas en `docs/capturas/`.

| Código | Cuerpo enviado | Respuesta | Capa que respondió | Captura |
|---|---|---|---|---|
| 201 | `{"cliente_id":1,"items":[{"producto_id":4,"cantidad":1}]}` | `{"id":8,"cliente_id":1,"estado":"pendiente","total":11.0}` | **Mi código** valida y calcula el total; **la base** guarda el pedido y descuenta stock en una transacción. | [201](capturas/201.png) |
| 404 | `{"cliente_id":1,"items":[{"producto_id":999,"cantidad":1}]}` | `{"detail":"Producto 999 no existe"}` | **Mi código**: `app/pedidos.py` línea 22 (`HTTPException(404)`) al no encontrar el producto en la base. | [404](capturas/404.png) |
| 409 | `{"cliente_id":1,"items":[{"producto_id":8,"cantidad":10}]}` | `{"detail":"Stock insuficiente para producto 8"}` | **Mi código**: `app/pedidos.py` línea 24 compara stock (5) con cantidad (10). | [409](capturas/409.png) |
| 422 | `{"cliente_id":1,"items":[{"producto_id":1,"cantidad":0}]}` | `{"detail":[{"type":"greater_than","loc":["body","items",0,"cantidad"],"msg":"Input should be greater than 0",...}]}` | **FastAPI/Pydantic**: `Field(gt=0)` en `app/modelos.py`. Mi función ni se ejecuta. | [422](capturas/422.png) |

Cómo distinguir la capa:
- **422 con `detail` en forma de lista** (`type`, `loc`, `msg`) → lo generó Pydantic al validar la entrada, antes de mi código. Swagger lo muestra como *Validation Error* documentado.
- **`detail` como texto propio** ("Producto 999 no existe") → lo escribí yo con `HTTPException`. Swagger marca 404 y 409 como ***Undocumented***: FastAPI no los conoce porque salen de mi código y no los declaré en `responses=`.
- **La base** no respondió ninguno de estos cuatro de forma directa: sus `CHECK`/`UNIQUE`/FK son la última defensa. Si una regla solo la frena la base, FastAPI responde **500** (por ejemplo, un pedido con el mismo producto en dos líneas que juntas superan el stock).
