from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.core.config import settings
from app.infrastructure.github_client import GithubAdapter
from app.rag.indexer import CodeIndexer

logger = logging.getLogger(__name__)
router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str

@router.post("/ingest")
async def ingest_repository(request: IngestRequest) -> Dict[str, Any]:
    """
    Orchestrates the extraction of code from GitHub and its indexing into Neo4j.
    """
    repo_url = request.repo_url
    
    try:
        # 1. Infrastructure: Extract code from GitHub
        # We instantiate the adapter with the token from settings
        github_adapter = GithubAdapter(github_token=settings.GITHUB_TOKEN)
        code_files = await github_adapter.extract_repo(repo_url)
        
        # Extract a simple name for the repository from the URL for the indexer
        # Example: 'https://github.com/owner/repo' -> 'owner/repo'
        repo_name = repo_url.rstrip("/").split("/")[-2:]
        repo_identifier = "/".join(repo_name) if len(repo_name) == 2 else repo_url

        # 2. RAG Core: Index the extracted files into Neo4j
        indexer = CodeIndexer()
        indexer.index_repository(repository_name=repo_identifier, code_files=code_files)
        
        return {
            "message": "Ingesta completada",
            "files_processed": len(code_files),
            "repository": repo_identifier
        }

    except ValueError as ve:
        logger.error(f"Validation error during ingestion: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except ConnectionError as ce:
        logger.error(f"Infrastructure connection error: {str(ce)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=str(ce)
        )
    except Exception as e:
        logger.error(f"Unexpected error during ingestion of {repo_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {str(e)}"
        )
