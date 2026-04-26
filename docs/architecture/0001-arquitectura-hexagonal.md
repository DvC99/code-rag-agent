# ADR 0001: Adopción de Arquitectura Hexagonal

## Resumen
Se implementa la Arquitectura Hexagonal (puertos y adaptadores) para el proyecto Code-RAG con el objetivo de desacoplar la lógica de negocio y la orquestación de IA de los detalles técnicos de infraestructura.

## Justificación
La naturaleza de un sistema RAG implica una alta volatilidad en las herramientas utilizadas (cambios de LLMs, bases de datos vectoriales o APIs de extracción de código). El uso de arquitectura hexagonal permite:
- **Aislamiento del Core:** La lógica de análisis de código y RAG no depende de si la API es FastAPI o si los datos provienen de GitHub o GitLab.
- **Facilidad de Testing:** Permite mockear adaptadores de infraestructura sin afectar el dominio.
- **Mantenibilidad:** Cambios en la base de datos (ej. migrar de Neo4j a otra base de grafos) solo afectan a la capa de infraestructura.

## Definición de Capas

### 1. Domain (`app/domain`)
Contiene la lógica de negocio pura y las entidades del sistema. 
- **Responsabilidad:** Definir los modelos de datos (POJOs/Entities) y las interfaces (puertos) que el sistema requiere.
- **Restricción:** No debe tener dependencias de ninguna otra capa ni de librerías externas complejas (solo Pydantic para validación).

### 2. Infrastructure (`app/infrastructure`)
Implementa los adaptadores técnicos para servicios externos.
- **Responsabilidad:** Comunicación con APIs (GitHub), Bases de Datos (Neo4j) y sistemas de archivos.
- **Restricción:** Implementa las interfaces definidas en la capa de dominio.

### 3. RAG (`app/rag`)
Capa de orquestación y lógica de IA.
- **Responsabilidad:** Implementar el flujo de indexación, chunking, recuperación de contexto y generación de respuestas.
- **Restricción:** Coordina la interacción entre los adaptadores de infraestructura y el dominio.

### 4. App (`app/api`)
Capa de entrada o adaptadores de entrada.
- **Responsabilidad:** Exponer la funcionalidad a través de endpoints REST (FastAPI), manejar el ciclo de vida de las peticiones y la validación de esquemas.
- **Restricción:** No debe contener lógica de negocio; solo delega la ejecución a la capa RAG o Domain.
