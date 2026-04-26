import logging
import asyncio
from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from app.domain.models import CodeFile
from app.infrastructure.neo4j_store import Neo4jAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)

class CodeIndexer:
    """
    Handles the indexing of source code into a hybrid Vector-Graph store using LlamaIndex and Neo4j.
    Configured to use Gemini 1.5 Flash and text-embedding-004.
    """

    def __init__(self, neo4j_adapter: Neo4jAdapter) -> None:
        # 1. Configure LlamaIndex Global Settings for code chunking
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        # 2. Explicitly configure Gemini 1.5 models to avoid deprecation errors (404)
        try:
            # Using gemini-1.5-flash: Extremely fast and optimized for RAG
            Settings.llm = Gemini(
                model="models/gemini-1.5-flash", 
                api_key=settings.GOOGLE_API_KEY
            )
            
            # Using text-embedding-004: The latest Google embedding model (dimension 768)
            Settings.embed_model = GeminiEmbedding(
                model_name="models/text-embedding-004",
                api_key=settings.GOOGLE_API_KEY
            )
            logger.info("LlamaIndex configured with Gemini 1.5 Flash and text-embedding-004.")
        except Exception as e:
            logger.error(f"Failed to configure Google AI models: {str(e)}")
            raise RuntimeError(f"Google AI configuration failed: {str(e)}")

        self._vector_store = neo4j_adapter.get_vector_store()
        self._batch_size = 50 
        logger.info("CodeIndexer initialized with batch processing and Gemini 1.5.")

    async def index_repository(self, repository_name: str, code_files: List[CodeFile]) -> None:
        """
        Indexes a list of CodeFiles. 
        Offloads the heavy VectorStoreIndex creation to a separate thread to prevent blocking the event loop.
        """
        if not code_files:
            logger.warning("No files provided for indexing.")
            return

        try:
            logger.info(f"Indexing {len(code_files)} files for repository: {repository_name}...")
            
            documents = []
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
            
            storage_context = StorageContext.from_defaults(vector_store=self._vector_store)

            # Offload to thread to avoid blocking FastAPI
            await asyncio.to_thread(
                VectorStoreIndex.from_documents,
                documents,
                storage_context=storage_context
            )
            logger.info("Indexación completada exitosamente con Gemini 1.5.")
        except Exception as e:
            logger.error(f"Indexing failed for repository {repository_name}: {str(e)}")
            raise RuntimeError(f"An error occurred while indexing the repository: {str(e)}") from e
