from fastapi import FastAPI
from app.config import settings
from app.api.v1 import health

# This is the core FastAPI application object.

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Register each router with a URL prefix.
# The health router's GET "/health" becomes GET "/api/v1/health"

app.include_router(health.routers, prefix="/api/v1")

# Root
@app.get("/", tags=["ROOT"])
def root():
    """Friendly root message — handy to confirm the server is reachable."""
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}
