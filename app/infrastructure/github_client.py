import asyncio
import logging
from typing import List
from github import Github, GithubException
from app.domain.models import CodeFile

logger = logging.getLogger(__name__)

class GithubAdapter:
    """
    Adapter for interacting with the GitHub API using PyGithub.
    Handles the extraction of source code files from a given repository.
    """

    def __init__(self, github_token: str) -> None:
        self._token = github_token
        self._gh = Github(self._token)
        self._allowed_extensions = {".py", ".java", ".ts", ".js", ".md", ".html", ".css"}

    def _parse_repo_url(self, repo_url: str) -> str:
        """
        Extracts 'owner/repo' from a full GitHub URL.
        Example: 'https://github.com/owner/repo' -> 'owner/repo'
        """
        try:
            parts = repo_url.rstrip("/").split("/")
            if len(parts) < 2:
                raise ValueError("Invalid GitHub repository URL format.")
            return f"{parts[-2]}/{parts[-1]}"
        except Exception as e:
            raise ValueError(f"Failed to parse repository URL: {e}")

    def _sync_extract(self, repo_full_name: str, target_branch: str) -> List[CodeFile]:
        """
        Synchronous implementation of the extraction logic to be run in a thread.
        """
        try:
            repo = self._gh.get_repo(repo_full_name)
            # Optimization: Get the recursive tree to identify all files in one call
            tree = repo.get_git_tree(sha=target_branch, recursive=True)
            
            code_files: List[CodeFile] = []
            
            for item in tree:
                if item.type == "blob":
                    path = item.path
                    if any(path.endswith(ext) for ext in self._allowed_extensions):
                        # Fetch the actual file content
                        content_file = repo.get_contents(path, ref=target_branch)
                        
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
                raise Exception(f"Repository {repo_full_name} not found.") from ge
            if ge.status == 401:
                raise Exception("Invalid or expired GitHub token.") from ge
            raise Exception(f"GitHub API error: {ge.data.get('message', str(ge))}") from ge
        except Exception as e:
            raise Exception(f"Unexpected error during repository extraction: {e}") from e

    async def extract_repo(self, repo_url: str, target_branch: str = 'main') -> List[CodeFile]:
        """
        Asynchronously extracts supported source files from a GitHub repository.
        Uses asyncio.to_thread to avoid blocking the FastAPI event loop.
        """
        repo_full_name = self._parse_repo_url(repo_url)
        logger.info(f"Starting extraction for {repo_full_name} on branch {target_branch}...")
        
        try:
            # Offload the synchronous PyGithub calls to a separate thread
            files = await asyncio.to_thread(self._sync_extract, repo_full_name, target_branch)
            logger.info(f"Successfully extracted {len(files)} files from {repo_full_name}.")
            return files
        except Exception as e:
            logger.error(f"Extraction failed for {repo_url}: {str(e)}")
            raise e
