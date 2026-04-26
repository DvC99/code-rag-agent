import logging
from llama_index.core import VectorStoreIndex
from app.core.config import settings

logger = logging.getLogger(__name__)

class CodeQueryEngine:
    def __init__(self, index: VectorStoreIndex = None):
        self.index = index

    def query(self, question: str) -> str:
        """
        Queries the vector index to find relevant code fragments and generate an answer.
        """
        if not self.index:
            return "No index available. Please index a repository first."

        try:
            query_engine = self.index.as_query_engine()
            response = query_engine.query(question)
            return str(response)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"An error occurred during the query: {str(e)}"
