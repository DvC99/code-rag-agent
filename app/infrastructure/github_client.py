import asyncio
import logging
from typing import List
from github import Github, GithubException
from app.core.config import settings
from app.domain.models import CodeFile
from app.infrastructure.exceptions import (
    GitHubClientError,
    RepositoryNotFoundError,
    InvalidTokenError,
    GitHubApiError
)

logger = logging.getLogger(__name__)

class GithubAdapter:
    """
    Adapter for interacting with GitHub API using PyGithub.
    Since PyGithub is synchronous, I/O operations are offloaded to threads.
    """

    def __init__(self) -> None:
        self._gh = Github(settings.GITHUB_TOKEN)
        self._allowed_extensions = {".py", ".java", ".ts", ".js", ".md"}

    def _parse_repo_url(self, repo_url: str) -> str:
        """Extracts 'owner/repo' from a GitHub URL."""
        try:
            parts = repo_url.rstrip("/").split("/")
            if len(parts) < 2:
                raise GitHubClientError("Invalid repository URL format.")
            return f"{parts[-2]}/{parts[-1]}"
        except Exception as e:
            raise GitHubClientError(f"Failed to parse repository URL: {e}")

    def _sync_fetch_contents(self, repo_full_name: str) -> List[CodeFile]:
        """Synchronous implementation of content fetching."""
        try:
            repo = self._gh.get_repo(repo_full_name)
            # Optimization: recursive tree to get all paths in one call
            tree = repo.get_git_tree(recursive=True)
            
            code_files: List[CodeFile] = []
            
            for item in tree:
                if item.type == "blob":
                    path = item.path
                    if any(path.endswith(ext) for ext in self._allowed_extensions):
                        # Fetch file content
                        content_file = repo.get_contents(path)
                        code_files.append(
                            CodeFile(
                                path=path,
                                content=content_file.decoded_content.decode("utf-8"),
                                language=content_file.language or "Unknown",
                                metadata={"sha": item.sha}
                            )
                        )
            
            return code_files

        except GithubException as ge:
            if ge.status == 404:
                raise RepositoryNotFoundError(f"Repository {repo_full_name} not found.") from ge
            if ge.status == 401:
                raise InvalidTokenError("Invalid or expired GitHub token.") from ge
            raise GitHubApiError(f"GitHub API error: {ge.data.get('message', str(ge))}") from ge
        except Exception as e:
            raise GitHubClientError(f"Unexpected error fetching repository: {e}") from e

    async def fetch_repository_contents(self, repo_url: str) -> List[CodeFile]:
        """
        Asynchronously fetches all supported source files from a GitHub repository.
        """
        repo_full_name = self._parse_repo_url(repo_url)
        logger.info(f"Fetching contents for repository: {repo_full_name}")
        
        # Offload synchronous PyGithub calls to a separate thread to avoid blocking the event loop
        return await asyncio.to_thread(self._sync_fetch_contents, repo_full_name)
