import logging
from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from app.domain.models import CodeFile
from app.infrastructure.neo4j_store import Neo4jAdapter

logger = logging.getLogger(__name__)

class CodeIndexer:
    """
    Handles the indexing of source code into a hybrid Vector-Graph store using LlamaIndex and Neo4j.
    """

    def __init__(self, neo4j_adapter: Neo4jAdapter) -> None:
        # Configure LlamaIndex Global Settings for code chunking
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        # Dependency Injection: The vector store is provided by the adapter
        self._vector_store = neo4j_adapter.get_vector_store()
        logger.info("CodeIndexer initialized with Neo4j Vector Store.")

    async def index_repository(self, repository_name: str, code_files: List[CodeFile]) -> None:
        """
        Processes a list of CodeFile entities and indexes them into the Neo4j vector store.
        """
        if not code_files:
            logger.warning("No files provided for indexing.")
            return

        try:
            logger.info(f"Indexing {len(code_files)} files for repository: {repository_name}...")
            
            # 1. Transform domain CodeFile into LlamaIndex Documents
            documents: List[Document] = []
            for file in code_files:
                doc = Document(
                    text=file.content,
                    metadata={
                        "file_path": file.path,
                        "language": file.language,
                        "repository_name": repository_name,
                        **file.metadata
                    }
                )
                documents.append(doc)

            # 2. Setup Storage Context with Neo4j
            storage_context = StorageContext.from_defaults(vector_store=self._vector_store)

            # 3. Create VectorStoreIndex from documents
            VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context
            )

            logger.info(f"Successfully indexed repository {repository_name} into Neo4j.")

        except Exception as e:
            logger.error(f"Indexing failed for repository {repository_name}: {str(e)}")
            raise RuntimeError(f"An error occurred while indexing the repository: {str(e)}") from e
