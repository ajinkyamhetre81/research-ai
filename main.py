from fastapi import FastAPI
from routes.website_routes import router as website_router
from routes.db_routes import router as db_router
from utils.loggers import get_logger
import routes.main_routes
import routes.doc_analysis_routes
from routes.llm_routes import router as llm_router

# Get a logger for this file
logger = get_logger(__name__)

app = FastAPI()

app.include_router(routes.main_routes.router)
app.include_router(routes.doc_analysis_routes.router, prefix="/api/v1", tags=["document-analysis"])
app.include_router(website_router, prefix="/api", tags=["Website Crawler"])
app.include_router(db_router, prefix="/api", tags=["Database"])
app.include_router(llm_router, prefix="/api", tags=["LLM Processing"])