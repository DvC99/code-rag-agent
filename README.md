# Code-RAG Agent: Graph & Vector RAG para Análisis de Repositorios

Este proyecto implementa un sistema de Generación Aumentada por Recuperación (RAG) híbrido, diseñado específicamente para ingerir, analizar y razonar sobre repositorios de código fuente. 

A diferencia de los sistemas RAG tradicionales basados únicamente en similitud semántica (vectores), esta solución integra **GraphRAG** utilizando Neo4j para mapear las dependencias estructurales del código (nodos y relaciones), permitiendo a los LLMs comprender la arquitectura de software, trazar planes de desarrollo cross-repositorio y analizar el impacto de nuevas funcionalidades.

## 🏗️ Arquitectura del Sistema

El proyecto sigue los principios de **Arquitectura Hexagonal (Puertos y Adaptadores)** para mantener la lógica de IA y de negocio completamente aislada de los detalles de infraestructura (APIs externas, bases de datos, frameworks web).

### Tech Stack Principal
* **Lenguaje:** Python 3.10+
* **Framework Web:** FastAPI (backend asíncrono y ligero)
* **Motor RAG / Orquestación:** LlamaIndex (optimizado para integraciones Graph+Vector)
* **Base de Datos:** Neo4j con APOC (almacenamiento híbrido de grafos e índices vectoriales)
* **Extracción de Código:** PyGithub (interacción directa con la API de GitHub)
* **LLM Core:** OpenAI GPT-4o / Anthropic Claude 3.5 Sonnet (vía API)

## 📂 Estructura del Proyecto

```text
code-rag-agent/
├── app/
│   ├── api/                   # (Adaptadores de Entrada) Endpoints REST y schemas Pydantic
│   ├── core/                  # Configuraciones globales y carga de variables de entorno
│   ├── domain/                # (Core) Entidades de dominio (Repository, CodeNode, GraphEdge)
│   ├── infrastructure/        # (Adaptadores de Salida) Clientes de GitHub y Neo4j
│   ├── rag/                   # Casos de uso: Lógica de chunking, indexación y query engine
│   └── main.py                # Entrypoint de la aplicación FastAPI
├── docker-compose.yml         # Orquestación de infraestructura local (Neo4j)
├── requirements.txt           # Dependencias del proyecto
├── .env.example               # Plantilla de variables de entorno requeridas
└── README.md
```

## 🚀 Guía de Inicio Rápido (MVP - Iteración 1)

### 1. Requisitos Previos
* Docker y Docker Compose instalados.
* Python 3.10 o superior.
* Un **Personal Access Token (PAT)** de GitHub.
* Una API Key válida de tu proveedor de LLM (OpenAI o Anthropic).

### 2. Configuración del Entorno
Clona este repositorio y configura las variables de entorno:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:
```env
# GitHub
GITHUB_TOKEN=tu_personal_access_token

# LLM Provider
OPENAI_API_KEY=tu_api_key_aqui
# ANTHROPIC_API_KEY=tu_api_key_aqui

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password_seguro
```

### 3. Levantar la Infraestructura (Base de Datos)
Inicia el contenedor de Neo4j (que incluye las librerías APOC necesarias para el procesamiento de grafos de LlamaIndex):

```bash
docker-compose up -d
```
*La interfaz web de Neo4j estará disponible en `http://localhost:7474`.*

### 4. Instalación de Dependencias e Inicio del Servidor
Crea un entorno virtual, instala las dependencias y levanta la API:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*La documentación interactiva de la API estará disponible en `http://localhost:8000/docs`.*

## 🗺️ Roadmap de Iteraciones

* **Iteración 1 (Vectorial + Extracción Base):** Integración de `PyGithub` para clonar repositorios en memoria, aplicar *chunking* limpio a archivos `.py`, `.java` o `.ts` y realizar búsquedas vectoriales básicas.
* **Iteración 2 (GraphRAG):** Activación de Neo4j para extracción de dependencias. El LLM identificará relaciones entre clases, funciones y *endpoints* durante la fase de ingesta para construir el grafo de conocimiento.
* **Iteración 3 (Agentes Planificadores):** Implementación de lógica de agentes (*Query Engine*) capaz de ingerir múltiples repositorios (ej. Front y Back) en paralelo y responder a consultas complejas de arquitectura y planificación de desarrollo.
* **Iteración 4 (Opcional):** Exposición del sistema a través del protocolo MCP (Model Context Protocol) para permitir que IDEs u otras IAs consuman el grafo arquitectónico generado.

## 🛡️ Principios de Diseño
* **Agnóstico a la Base de Datos:** Los adaptadores deben permitir cambiar Neo4j por otra base híbrida sin reescribir los módulos de RAG.
* **Prioridad en el Contexto:** El código fuente no es texto plano; es una estructura jerárquica. Las estrategias de partición (*chunking*) deben respetar los límites de clases y funciones (ej. uso de analizadores AST si es necesario).
