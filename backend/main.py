"""
FastAPI Main Application Gateway
Initializes database connections, configures CORS, includes routers,
and starts the REST API server.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from database.connection import init_db
from api.middleware import AuditMiddleware

# Import routes
from api.routes import dataset, eda, predictions, reports, collections, chat, settings as settings_route

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production backend API for AI Financial Risk & Collections Assistant",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Audit Middleware
app.add_middleware(AuditMiddleware)

# Initialize Database tables
@app.on_event("startup")
def startup_db_init():
    init_db()

# Mount Static File directories for report/chart retrieval
app.mount("/static/reports", StaticFiles(directory=str(settings.REPORTS_DIR)), name="reports")
app.mount("/static/charts", StaticFiles(directory=str(settings.CHARTS_DIR)), name="charts")

# Health Check Route
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Register Sub-Routers
app.include_router(dataset.router, prefix="/api")
app.include_router(eda.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(collections.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(settings_route.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
