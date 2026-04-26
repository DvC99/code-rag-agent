from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProcessingStatus(str, Enum):
    """Track the state of the repository ingestion process."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class RepositoryInfo(BaseModel):
    """Metadata of the GitHub repository to be analyzed."""
    url: str = Field(..., description="The HTML URL of the repository")
    owner: str = Field(..., description="The login name of the repository owner")
    name: str = Field(..., description="The name of the repository")
    branch: str = Field(default="main", description="The branch to analyze")

class CodeFile(BaseModel):
    """Representation of a single source code file."""
    path: str = Field(..., description="The relative path of the file in the repository")
    content: str = Field(..., description="The raw content of the file")
    language: str = Field(..., description="The programming language of the file")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional file metadata")
