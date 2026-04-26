import logging
import asyncio
from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.google import GooglePaLMEmbedding
from llama_index.llms.google import Gemini
from app.domain.models import CodeFile
from app.infrastructure.neo4j_store import Neo4jAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)

class CodeIndexer:
    """
    Handles the indexing of source code into a hybrid Vector-Graph store using LlamaIndex and Neo4j.
    Configured to use Google Gemini for embeddings and LLM.
    """

    def __init__(self, neo4j_adapter: Neo4jAdapter) -> None:
        # 1. Configure LlamaIndex Global Settings for code chunking
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50
        
        # 2. Configure Google Gemini with explicit model names to avoid 404s
        try:
            # Use 'models/gemini-pro' explicitly as it is the most stable
            Settings.llm = Gemini(
                model_name="models/gemini-pro", 
                api_key=settings.GOOGLE_API_KEY
            )
            
            # Use GooglePaLMEmbedding (which typically maps to the stable embedding model)
            Settings.embed_model = GooglePaLMEmbedding(
                api_key=settings.GOOGLE_API_KEY
            )
            logger.info("LlamaIndex configured with explicit Google Gemini models.")
        except Exception as e:
            logger.error(f"Failed to configure Google AI: {str(e)}")
            raise RuntimeError(f"Google API configuration failed: {str(e)}")

        self._vector_store = neo4j_adapter.get_vector_store()
        self._batch_size = 50 
        logger.info("CodeIndexer initialized with batch processing and Google AI.")

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
            logger.info("Indexación completada exitosamente con Google AI.")
        except Exception as e:
            logger.error(f"Indexing failed for repository {repository_name}: {str(e)}")
            raise RuntimeError(f"An error occurred while indexing the repository: {str(e)}") from e
