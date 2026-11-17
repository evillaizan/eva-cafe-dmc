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