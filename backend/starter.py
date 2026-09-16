import os
import logging
from fastapi import FastAPI
from backend.config.database_config import engine, Base
from backend.config.env_config import settings
from backend.routes.api_routes import router as api_router
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.exceptions import (
    BaseAppException,
    app_exception_handler,
    global_exception_handler,
    http_exception_handler,
    request_validation_handler,
)

logger = logging.getLogger("productivityAssistant")

class AppStarter:
    """Core starter for the application that initializes databases, routes, and workflows."""
    
    def __init__(self):
        self.app = FastAPI(title=settings.PROJECT_NAME)
        self._initialize_database()
        self._register_routes()
        self._register_exception_handlers()
        
    def _initialize_database(self):
        """Creates database tables if they do not exist."""
        logger.info(f"Initializing database at {settings.DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        
    def _register_routes(self):
        """Registers the FastAPI routers."""
        logger.info("Registering API routes")
        self.app.include_router(api_router)
        
    def _register_exception_handlers(self):
        """Registers global exception handlers for the FastAPI app."""
        logger.info("Registering Global Exception Handlers")
        self.app.add_exception_handler(RequestValidationError, request_validation_handler)
        self.app.add_exception_handler(StarletteHTTPException, http_exception_handler)
        self.app.add_exception_handler(BaseAppException, app_exception_handler)
        self.app.add_exception_handler(Exception, global_exception_handler)
        
    def get_app(self) -> FastAPI:
        """Returns the configured FastAPI application instance."""
        return self.app
