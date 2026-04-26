from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from dotenv import load_dotenv

# Cargar variables de entorno al iniciar
load_dotenv()

app = FastAPI(title="Code-RAG API", version="0.1.0")

# Prevención del error "Failed to fetch" por CORS en el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos las rutas
app.include_router(router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Code-RAG API funcionando"}
