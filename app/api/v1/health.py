from fastapi import APIRouter
from app.config import settings


routers = APIRouter(tags=["Health"])

@routers.get("/health")
def health_check():
    """
    A simple liveness probe.
 
    Use cases:
    - Verify the server is running during development
    - Load balancers / container orchestrators (e.g. Kubernetes) ping this
      to know if the service is alive before routing traffic to it
 
    Returns basic app info — never sensitive data.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }
