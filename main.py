from fastapi import FastAPI
from utils.loggers import get_logger, log_with_context, log_operation_start, log_operation_end, log_user_action
import time
import routes.main_routes
import routes.doc_analysis_routes
# Get a logger for this file
logger = get_logger(__name__)

app = FastAPI()

app.include_router(routes.main_routes.router)
app.include_router(routes.doc_analysis_routes.router, prefix="/api/v1", tags=["document-analysis"])
