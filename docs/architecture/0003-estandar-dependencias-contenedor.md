# ADR 0003: Estandar de Dependencias para Contenedor

## Resumen
Se define un estandar unico de versionado de dependencias para la ejecucion en Docker, priorizando `requirements.txt` como fuente de verdad para la imagen de runtime y manteniendo compatibilidad explicita entre FastAPI, Pydantic y LlamaIndex.

## Problema
Durante la reconstruccion del servicio `api` se presentaron fallas de arranque por inconsistencia entre paquetes instalados y paquetes importados en el codigo:
1. **Dependencia faltante en runtime:** La imagen no incluia el plugin de vector store para Neo4j requerido por el import de `Neo4jVectorStore`.
2. **Divergencia entre archivos de dependencias:** `pyproject.toml` y `requirements.txt` tenian versiones no alineadas.
3. **Conflicto de resolucion de pip:** Versiones recientes de LlamaIndex requerian un rango de Pydantic distinto al fijado por el proyecto.

## Decision
Se adopta la siguiente politica:
- **Fuente de verdad en contenedor:** `requirements.txt` gobierna la instalacion en Docker.
- **Compatibilidad fijada:** Se mantienen versiones compatibles entre si para evitar `ResolutionImpossible` y errores de importacion.
- **Plugin vectorial obligatorio:** El paquete `llama-index-vector-stores-neo4jvector` es requerido cuando exista uso de `llama_index.vector_stores.neo4jvector` en el codigo.

Versiones estabilizadas para runtime:
- `llama-index==0.10.43`
- `llama-index-graph-stores-neo4j==0.1.4`
- `llama-index-vector-stores-neo4jvector==0.1.4`
- `pydantic==2.7.4`
- `pydantic-settings==2.3.4`

## Consecuencias
- **Positivas:**
  - Arranque estable del servicio `api` en Docker.
  - Eliminacion del `ModuleNotFoundError` asociado a `llama_index.vector_stores`.
  - Menor riesgo de conflictos de resolucion en builds futuros.
- **Negativas:**
  - Se limita temporalmente la adopcion de versiones mas nuevas de LlamaIndex hasta planificar una migracion completa de dependencias.

## Lineamientos Operativos
1. Cualquier actualizacion de LlamaIndex debe validarse junto con FastAPI/Pydantic en un build limpio de Docker.
2. Si se modifica `pyproject.toml`, se debe reflejar explicitamente la estrategia equivalente en `requirements.txt` para runtime.
3. Antes de mergear cambios de dependencias, ejecutar:
   - `docker compose down --remove-orphans`
   - `docker compose up -d --build`
   - `docker compose ps`
   - `docker compose logs --tail 80 api`
