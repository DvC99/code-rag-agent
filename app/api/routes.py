from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.infrastructure.github_client import GithubAdapter
from app.infrastructure.neo4j_store import Neo4jAdapter
from app.rag.indexer import CodeIndexer

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str

@router.post("/ingest")
async def ingest_repo(request: IngestRequest):
    try:
        # 1. Extracción (GitHub)
        token = settings.GITHUB_TOKEN
        github_adapter = GithubAdapter(github_token=token)
        code_files = await github_adapter.extract_repo(request.repo_url)
        
        # 2. Base de Datos e Indexación (Neo4j + LlamaIndex)
        neo4j_adapter = Neo4jAdapter()
        indexer = CodeIndexer(neo4j_adapter)
        
        await indexer.index_repository(code_files)
        
        return {
            "message": "Ingesta y vectorización completada", 
            "files_processed": len(code_files)
        }
    except Exception as e:
        # Capturamos cualquier error y lo devolvemos como 500
        raise HTTPException(status_code=500, detail=str(e))
