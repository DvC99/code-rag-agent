import logging
from llama_index.vector_stores.neo4j import Neo4jVectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jAdapter:
    """
    Adapter for managing the connection to Neo4j database.
    Decouples the database infrastructure from the RAG logic.
    """

    def __init__(self) -> None:
        self._uri = settings.NEO4J_URI
        self._username = settings.NEO4J_USERNAME
        self._password = settings.NEO4J_PASSWORD

        if not all([self._uri, self._username, self._password]):
            logger.error("Neo4j credentials are missing in environment variables.")
            raise ConnectionError("Neo4j configuration is incomplete. Check your .env file.")

    def get_vector_store(self) -> Neo4jVectorStore:
        """
        Instantiates and returns a Neo4jVectorStore.
        Using embedding_dimension=1536 for OpenAI embeddings.
        """
        try:
            logger.info(f"Initializing Neo4jVectorStore connection to {self._uri}...")
            vector_store = Neo4jVectorStore(
                url=self._uri,
                username=self._username,
                password=self._password,
                embedding_dimension=1536
            )
            return vector_store
        except Exception as e:
            logger.error(f"Failed to initialize Neo4jVectorStore: {str(e)}")
            raise ConnectionError(f"Could not establish Neo4j Vector Store connection: {str(e)}") from e
