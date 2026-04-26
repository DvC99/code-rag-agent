# ADR 0002: Enfoque de RAG Híbrido (Grafo + Vector)

## Problema
Los sistemas RAG tradicionales basados exclusivamente en similitud vectorial (Dense Retrieval) presentan limitaciones críticas al analizar código fuente:
1. **Pérdida de Contexto Estructural:** Un vector representa el significado semántico de un fragmento, pero ignora la jerarquía del software (ej. una función llama a otra, una clase hereda de otra).
2. **Dificultad en Consultas Globales:** Responder a preguntas como "¿Cómo fluye la autenticación en todo el proyecto?" requiere trazar dependencias, no solo encontrar fragmentos similares.

## Solución: RAG Híbrido
Code-RAG implementa un enfoque híbrido que combina la recuperación vectorial con la navegación en grafos de conocimiento.

### Componentes Clave
- **Vector Store:** Almacena embeddings de fragmentos de código para búsquedas semánticas rápidas (recuperación de "qué").
- **Graph Store (Neo4j):** Almacena la topología del código (Nodos: Clases, Funciones, Archivos; Relaciones: `CALLS`, `DEFINES`, `INHERITS`, `IMPORTS`). Permite responder al "cómo" y "dónde" estructuralmente.

### Justificación de Herramientas
- **Neo4j:** Elegido por su capacidad de realizar consultas complejas de travesía (Cypher) y su soporte nativo para índices vectoriales, permitiendo que el grafo y el vector coexistan en el mismo motor.
- **LlamaIndex:** Proporciona la abstracción necesaria para integrar `KnowledgeGraphIndex` y `VectorStoreIndex`, facilitando la orquestación de la recuperación híbrida.

## Flujo de Recuperación
1. **Búsqueda Vectorial:** Se identifican los nodos de código más relevantes semánticamente.
2. **Expansión de Grafo:** A partir de esos nodos, se navega por el grafo de Neo4j para extraer el contexto estructural circundante (dependencias directas e indirectas).
3. **Síntesis:** El LLM recibe tanto el fragmento de código como su ubicación y relaciones en la arquitectura, generando una respuesta precisa y contextualmente rica.
