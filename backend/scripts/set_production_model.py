from app.db.session import SessionLocal
from app.models.model_registry import ModelRegistry


def main():
    db = SessionLocal()

    try:
        models = db.query(ModelRegistry).all()

        for model in models:
            if model.version == "v2.0":
                model.status = "ACTIVE"
            elif model.version == "v2.1-candidate":
                model.status = "CANDIDATE"
            else:
                model.status = "ARCHIVED"

        db.commit()

        active = (
            db.query(ModelRegistry)
            .filter(ModelRegistry.status == "ACTIVE")
            .first()
        )

        print("Production model configured successfully.")
        print(f"ACTIVE: {active.version}")
        print(f"MODEL PATH: {active.model_path}")

    finally:
        db.close()


if __name__ == "__main__":
    main()