import logging

from llama_index.vector_stores.neo4jvector import Neo4jVectorStore

from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jAdapter:
    """Adaptador para la conexión con la base de datos Neo4j."""
    
    def __init__(self) -> None:
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD

    def get_vector_store(self) -> Neo4jVectorStore:
        try:
            vector_store = Neo4jVectorStore(
                url=self.uri,
                username=self.username,
                password=self.password,
                embedding_dimension=1536,
                index_name="code_index",
                node_label="CodeChunk",
                text_node_property="text"
            )
            logger.info("Conexión a Neo4j Vector Store instanciada.")
            return vector_store
        except Exception as e:
            logger.error(f"Fallo al conectar con Neo4j: {str(e)}")
            raise
