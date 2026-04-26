# Estándares de Codificación Python - Code-RAG

Este documento define las reglas obligatorias de desarrollo para asegurar la calidad, mantenibilidad y escalabilidad del proyecto.

## 1. Tipado Estricto (Type Hinting)
El uso de Type Hints es **obligatorio** en todas las definiciones de funciones y métodos.
- Se deben definir tipos de entrada y de retorno.
- Para colecciones, usar `typing.List`, `typing.Dict`, `typing.Optional`, etc.
- **Ejemplo:**
  ```python
  async def fetch_repository_contents(self, repo_url: str) -> List[CodeFile]:
  ```

## 2. Asincronía y Operaciones de I/O
Para evitar el bloqueo del event loop de FastAPI, todas las operaciones de entrada/salida deben ser asíncronas.
- Usar `async def` y `await` para llamadas a APIs, bases de datos y sistema de archivos.
- En caso de usar librerías síncronas (ej. `PyGithub`), se debe delegar la ejecución a hilos mediante `asyncio.to_thread`.

## 3. Gestión de Dependencias
El proyecto utiliza **Poetry** para la gestión de dependencias y entornos virtuales.
- No se debe usar `pip install` directamente en el entorno de desarrollo.
- Cualquier nueva dependencia debe agregarse vía `poetry add <package>`.
- El archivo `pyproject.toml` es la única fuente de verdad para las versiones de las librerías.

## 4. Validación de Datos y Modelos
Se utiliza **Pydantic v2** para todas las entidades de dominio y esquemas de API.
- Definir modelos heredando de `BaseModel`.
- Usar `Field` para añadir descripciones y validaciones a los atributos.
- El uso de diccionarios genéricos (`Dict[str, Any]`) debe minimizarse en favor de modelos tipados.

## 5. Inyección de Dependencias (DI)
Para mantener la arquitectura hexagonal y facilitar el testing:
- Los adaptadores de infraestructura deben inyectarse en los controladores de la API utilizando el sistema de `Depends` de FastAPI.
- Evitar la instanciación directa de clases de infraestructura dentro de la lógica de negocio.

## 6. Manejo de Errores y Logging
- No utilizar bloques `try-except` genéricos que silencien errores.
- Definir excepciones personalizadas en la capa de infraestructura y capturarlas en la capa de aplicación para transformarlas en respuestas HTTP.
- Usar la librería `logging` de Python en lugar de `print()`.
