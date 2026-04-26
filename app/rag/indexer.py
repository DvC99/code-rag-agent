import logging
from typing import List
from llama_index.core import Document, VectorStoreIndex, Settings
from app.domain.models import CodeFile
from app.infrastructure.neo4j_store import Neo4jAdapter

logger = logging.getLogger(__name__)

class CodeIndexer:
    def __init__(self, neo4j_adapter: Neo4jAdapter):
        # Parámetros de chunking optimizados para código
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        # Inyección de dependencias
        self.vector_store = neo4j_adapter.get_vector_store()

    async def index_repository(self, code_files: List[CodeFile]) -> None:
        logger.info(f"Iniciando indexación de {len(code_files)} archivos...")
        
        documents = []
        for file in code_files:
            doc = Document(
                text=file.content,
                metadata={
                    "file_path": file.path,
                    "language": file.language,
                    "repository_name": file.repository_name
                }
            )
            documents.append(doc)
            
        try:
            VectorStoreIndex.from_documents(
                documents,
                vector_store=self.vector_store
            )
            logger.info("Indexación completada exitosamente.")
        except Exception as e:
            logger.error(f"Fallo durante la creación del índice vectorial: {str(e)}")
            raise
