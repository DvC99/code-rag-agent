class GitHubClientError(Exception):
    """Base exception for GitHub client errors."""
    pass

class RepositoryNotFoundError(GitHubClientError):
    """Raised when the specified repository is not found."""
    pass

class InvalidTokenError(GitHubClientError):
    """Raised when the GitHub token is invalid or expired."""
    pass

class GitHubApiError(GitHubClientError):
    """Raised when the GitHub API returns an unexpected error."""
    pass
