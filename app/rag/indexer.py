import logging
from llama_index.core import Document, VectorStoreIndex, StorageContext, ServiceContext
from llama_index.core.node_parser import TokenTextSplitter
from app.infrastructure.github_client import GitHubClient
from app.domain.models import CodeChunk, IndexingStatus
from app.core.config import settings

logger = logging.getLogger(__name__)

class CodeIndexer:
    def __init__(self):
        self.github_client = GitHubClient()
        # Simple splitter for now, will evolve to AST-based in future iterations
        self.splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)

    def index_repository(self, repo_full_name: str) -> IndexingStatus:
        """
        Fetches code from GitHub, chunks it, and creates a vector index.
        """
        try:
            documents = []
            files_processed = 0
            
            # 1. Extract contents
            for file_path, content in self.github_client.get_repo_contents(repo_full_name):
                # Create a LlamaIndex Document for each file
                doc = Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "repository": repo_full_name
                    }
                )
                documents.append(doc)
                files_processed += 1

            # 2. Chunk and Index
            index = VectorStoreIndex.from_documents(documents)
            
            return index, IndexingStatus(
                repository=repo_full_name,
                files_processed=files_processed,
                chunks_created=len(index.docstore.docs),
                status="completed"
            )

        except Exception as e:
            logger.error(f"Indexing failed for {repo_full_name}: {e}")
            return None, IndexingStatus(
                repository=repo_full_name,
                files_processed=0,
                chunks_created=0,
                status="failed",
                error=str(e)
            )
