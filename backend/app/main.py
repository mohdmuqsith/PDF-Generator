from app.api.health import router as health_router
from app.api.reports import router as reports_router
from fastapi import FastAPI

app = FastAPI(title="PDF Report Generator")

app.include_router(health_router)
app.include_router(reports_router)
