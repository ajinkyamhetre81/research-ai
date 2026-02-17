from fastapi import APIRouter
from utils.loggers import get_logger, log_with_context, log_operation_start, log_operation_end

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
def read_root():
    log_operation_start(logger, "Home page request")
    
    # Log with extra context
    log_with_context(
        logger, 
        "Processing home page request",
        extra_context={"endpoint": "/", "method": "GET"}
    )
    
    log_operation_end(logger, "Home page request", success=True)
    return {"message": "Welcome to Research AI"}
