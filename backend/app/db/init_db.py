from app.db.session import Base, engine
from app.models.core import Shipment
from app.models.decision import Decision
from app.models.outcome import DecisionOutcome
from app.models.model_registry import ModelRegistry

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")