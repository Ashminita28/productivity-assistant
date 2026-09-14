from backend.config.database_config import engine, Base
from backend.models.task import Task
from backend.config.log_config import logger

def init_db():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
