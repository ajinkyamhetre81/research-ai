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
                "model": "gemini-2.5-flash",
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
            "model": "gemini-2.5-flash",
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


@router.post("/llm-extract-faculty")
async def extract_faculty_with_llm(request: dict):
    """
    Extract faculty information from academic documents using LLM.
    
    Sample Request:
        POST /api/llm-extract-faculty
        Content-Type: application/json
        
        {
            "raw_data": "Stanford University Computer Science Department. Faculty: Prof. John Smith (john@stanford.edu) teaches AI and Machine Learning. Dr. Jane Doe (jane@cs.stanford.edu) teaches Algorithms and Data Structures. Contact: (650) 725-1234."
        }
    
    Sample Response:
        {
            "success": true,
            "processing_type": "faculty_extraction",
            "raw_data": "...",
            "processed_data": {
                "institution": {
                    "college_name": "Stanford University",
                    "website": "stanford.edu",
                    "address": "NA",
                    "contact_email": "NA",
                    "contact_phone": "NA"
                },
                "departments": [
                    {
                        "department_name": "Computer Science Department",
                        "department_email": "NA",
                        "department_phone": "NA",
                        "faculty_members": [
                            {
                                "full_name": "Prof. John Smith",
                                "designation": "Professor",
                                "subjects_taught": ["AI", "Machine Learning"],
                                "email": "john@stanford.edu",
                                "phone": "NA",
                                "office_address": "NA",
                                "profile_url": "NA"
                            },
                            {
                                "full_name": "Dr. Jane Doe",
                                "designation": "Professor",
                                "subjects_taught": ["Algorithms", "Data Structures"],
                                "email": "jane@cs.stanford.edu",
                                "phone": "(650) 725-1234",
                                "office_address": "NA",
                                "profile_url": "NA"
                            }
                        ]
                    }
                ],
                "extraction_metadata": {
                    "faculty_count": 2,
                    "department_count": 1,
                    "confidence_level": "high"
                }
            },
            "processing_time": 890,
            "model": "gemini-2.5-flash",
            "timestamp": 1645431234.567
        }
    """
    try:
        raw_data = request.get("raw_data", "")
        if not raw_data:
            raise HTTPException(
                status_code=400,
                detail="raw_data is required"
            )
        
        service = LLMService()
        result = service.process_faculty_extraction(raw_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Faculty extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Faculty extraction failed: {str(e)}"
        )
