from app.db.session import Base, engine
from app.models.core import Shipment


def init_db():
    Base.metadata.create_all(bind=engine)