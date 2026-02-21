# routes/llm_routes.py

from fastapi import APIRouter, HTTPException
from services.llm_service import LLMService
from utils.loggers import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/llm-status")
async def get_llm_status():
    """
    Get LLM service status.
    
    Sample Request:
        GET /api/llm-status
    
    Sample Response:
        {
            "success": true,
            "status": {
                "available": true,
                "model": "gemini-1.5-flash",
                "api_key_configured": true,
                "client_initialized": true,
                "library_version": "0.3.2"
            }
        }
    """
    try:
        service = LLMService()
        status = service.get_status()
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Failed to get LLM status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get LLM status: {str(e)}"
        )


@router.post("/llm-test")
async def test_llm_connection():
    """
    Test LLM API connection.
    
    Sample Request:
        POST /api/llm-test
    
    Sample Response:
        {
            "success": true,
            "response": "API connection successful!",
            "processing_time": 1250,
            "model": "gemini-1.5-flash",
            "timestamp": 1645431234.567
        }
    """
    try:
        service = LLMService()
        result = service.test_connection()
        
        return result
        
    except Exception as e:
        logger.error(f"LLM test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LLM test failed: {str(e)}"
        )
