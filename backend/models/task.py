from sqlalchemy import Column, Integer, String
from backend.config.database_config import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True, nullable=False)
    status = Column(String, default="Pending", nullable=False)
