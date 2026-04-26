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
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
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
        Validates that at least one critical LLM API key is present and GitHub token exists.
        """
        # GitHub token is always required
        if not cls.GITHUB_TOKEN:
            logger.critical("Missing critical environment variable: GITHUB_TOKEN")
            raise ValueError("Missing critical environment variable: GITHUB_TOKEN")

        # At least one LLM provider must be configured
        if not any([cls.OPENAI_API_KEY, cls.GOOGLE_API_KEY, cls.ANTHROPIC_API_KEY]):
            logger.critical("Missing critical environment variables: No LLM API key provided (OpenAI, Google, or Anthropic)")
            raise ValueError("No LLM API key provided. Please set OPENAI_API_KEY or GOOGLE_API_KEY in .env")
            
        logger.info("Environment configuration validated successfully.")

# Instantiate settings and perform immediate validation
settings = Settings()
settings.validate()
