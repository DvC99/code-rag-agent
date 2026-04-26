import logging
from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from app.domain.models import CodeFile
from app.core.config import settings

logger = logging.getLogger(__name__)

class CodeIndexer:
    """
    Handles the indexing of source code into a hybrid Vector-Graph store using LlamaIndex and Neo4j.
    """

    def __init__(self) -> None:
        # Configure LlamaIndex Global Settings for code chunking
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        try:
            # Initialize Neo4j Vector Store
            # LlamaIndex will use OpenAI embeddings by default if OPENAI_API_KEY is in .env
            self._vector_store = Neo4jVectorStore(
                url=settings.NEO4J_URI,
                username=settings.NEO4J_USERNAME,
                password=settings.NEO4J_PASSWORD
            )
            logger.info("Successfully connected to Neo4j Vector Store.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise ConnectionError(f"Could not establish connection to Neo4j at {settings.NEO4J_URI}") from e

    def index_repository(self, repository_name: str, code_files: List[CodeFile]) -> None:
        """
        Processes a list of CodeFile entities and indexes them into the Neo4j vector store.
        
        Args:
            repository_name: Name of the repository being indexed.
            code_files: List of CodeFile objects containing content and metadata.
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
            # This process: 
            # a) Chunks documents based on Settings.chunk_size
            # b) Generates embeddings via OpenAI (default)
            # c) Stores embeddings and nodes in Neo4j
            VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context
            )

            logger.info(f"Successfully indexed repository {repository_name} into Neo4j.")

        except Exception as e:
            logger.error(f"Indexing failed for repository {repository_name}: {str(e)}")
            raise RuntimeError(f"An error occurred while indexing the repository: {str(e)}") from e
