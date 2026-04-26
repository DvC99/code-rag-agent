import os
import logging
from dotenv import load_dotenv

# Setup logging for configuration errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Centralized configuration for the Code-RAG application.
    Handles environment variable loading and validation.
    """
    
    # GitHub Integration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # LLM Provider
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Neo4j Database
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password_seguro")
    
    # App settings
    APP_NAME: str = "Code-RAG Agent"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """
        Validates that all critical environment variables are present.
        Raises ValueError if any critical variable is missing.
        """
        critical_vars = {
            "GITHUB_TOKEN": cls.GITHUB_TOKEN,
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
        }
        
        missing_vars = [var for var, value in critical_vars.items() if not value]
        
        if missing_vars:
            error_msg = f"Missing critical environment variables: {', '.join(missing_vars)}"
            logger.critical(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Environment configuration validated successfully.")

# Instantiate settings and perform immediate validation
settings = Settings()
settings.validate()
