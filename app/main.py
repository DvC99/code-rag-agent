import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="Code-RAG API",
        description="Hybrid Graph and Vector RAG for software repository analysis",
        version="0.1.0"
    )

    # Configure CORS to allow requests from any origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the RAG orchestration routes
    app.include_router(api_router, prefix="/api", tags=["Ingestion"])

    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    # Start the server using uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )
