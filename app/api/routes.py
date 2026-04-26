from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.core.config import settings
from app.infrastructure.github_client import GithubAdapter
from app.infrastructure.neo4j_store import Neo4jAdapter
from app.rag.indexer import CodeIndexer

logger = logging.getLogger(__name__)
router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str

async def run_ingestion_pipeline(repo_url: str):
    """
    Background task to handle the full ingestion pipeline.
    Decouples the HTTP request from the heavy processing.
    """
    try:
        logger.info(f"Background pipeline started for {repo_url}")
        
        # 1. Extraction
        github_adapter = GithubAdapter(github_token=settings.GITHUB_TOKEN)
        code_files = await github_adapter.extract_repo(repo_url)
        
        # Extract repository identifier
        repo_name = repo_url.rstrip("/").split("/")[-2:]
        repo_identifier = "/".join(repo_name) if len(repo_name) == 2 else repo_url

        # 2. Indexing
        neo4j_adapter = Neo4jAdapter()
        indexer = CodeIndexer(neo4j_adapter=neo4j_adapter)
        await indexer.index_repository(repository_name=repo_identifier, code_files=code_files)
        
        logger.info(f"Background pipeline completed successfully for {repo_url}")
    except Exception as e:
        logger.error(f"Critical error in background ingestion pipeline for {repo_url}: {str(e)}")

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_repository(request: IngestRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Triggers the ingestion process in the background.
    Returns immediately to avoid HTTP timeouts.
    """
    repo_url = request.repo_url
    
    # Validate URL format quickly before starting background task
    if not repo_url.startswith("http"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL scheme")

    # Queue the heavy processing in the background
    background_tasks.add_task(run_ingestion_pipeline, repo_url)
    
    return {
        "status": "accepted",
        "message": "Ingestion started in background. The system is now extracting and indexing the repository.",
        "repository": repo_url
    }
