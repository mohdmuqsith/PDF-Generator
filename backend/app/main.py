from app.api.health import router as health_router  # noqa: I001
from app.api.reports import router as reports_router
from app.db.database import initialize_database

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF Report Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(reports_router)


@app.on_event("startup")
def on_startup():
    initialize_database()
