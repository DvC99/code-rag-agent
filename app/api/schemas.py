from pydantic import BaseModel
from typing import Optional

class IndexRequest(BaseModel):
    repo_full_name: str

class IndexResponse(BaseModel):
    repository: str
    files_processed: int
    chunks_created: int
    status: str
    error: Optional[str] = None

class QueryRequest(BaseModel):
    repo_full_name: str
    question: str

class QueryResponse(BaseModel):
    answer: str
