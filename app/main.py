from fastapi import FastAPI
from app.core.config import settings
from app.modules.health.routes import router as health_router

"""Main application entry point"""

app = FastAPI(title=settings.app_name)

app.include_router(health_router)

"""Root endpoint"""
@app.get("/")
async def root():
    return {"message": "API up", "docs": "/docs"}
