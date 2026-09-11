from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db

init_db()

app = FastAPI(
    title="Supply Prescript API",
    description="Closed-Loop Prescriptive Analytics Platform for Supply Chain Risk",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "supply-prescript-api",
        "version": "1.0.0",
    }