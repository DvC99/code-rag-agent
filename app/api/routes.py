from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.infrastructure.github_client import GithubAdapter
from app.infrastructure.exceptions import GitHubClientError, RepositoryNotFoundError, InvalidTokenError
from app.domain.models import CodeFile

router = APIRouter()

# Dependency Provider
def get_github_adapter() -> GithubAdapter:
    return GithubAdapter()

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_repository(
    repo_url: str, 
    adapter: GithubAdapter = Depends(get_github_adapter)
) -> Dict[str, Any]:
    """
    Ingests source code from a GitHub repository.
    V0.1: Simply extracts files and returns a summary.
    """
    try:
        files: List[CodeFile] = await adapter.fetch_repository_contents(repo_url)
        
        return {
            "status": "success",
            "files_count": len(files),
            "files": [file.path for file in files]
        }
    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=str(e)
        )
    except GitHubClientError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {str(e)}"
        )
