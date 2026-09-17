from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.predictions import router as prediction_router
from app.api.recommendations import router as recommendation_router
from app.api.decision import router as decision_router
from app.api.decisions import router as decision_write_router
from app.api.decision_history import router as decision_history_router
from app.api.execution import router as execution_router
from app.api.outcomes import router as outcome_router
from app.api.evaluation import router as evaluation_router
from app.api.evaluation_summary import (
    router as evaluation_summary_router,
)
from app.api.evaluation_history import (
    router as evaluation_history_router,
)

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


app.include_router(prediction_router)
app.include_router(recommendation_router)
app.include_router(decision_router)
app.include_router(decision_write_router)
app.include_router(decision_history_router)
app.include_router(execution_router)
app.include_router(outcome_router)
app.include_router(evaluation_router)
app.include_router(
    evaluation_summary_router
)
app.include_router(
    evaluation_history_router
)

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "supply-prescript-api",
        "version": "1.0.0",
    }