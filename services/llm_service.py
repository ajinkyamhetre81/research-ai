# services/llm_service.py

import os
import time
import json
from typing import Dict, Any, Optional
from utils.loggers import get_logger, log_operation_start, log_operation_end
from services.prompt_service import PromptService

try:
    from google import genai
except ImportError:
    genai = None

logger = get_logger(__name__)


class LLMService:
    """Simple LLM service for testing Google Generative AI API."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("MODEL_API_KEY")
        self.model_name = model_name or os.getenv("MODEL_NAME", "gemini-2.5-flash")
        self.client = None
        
        if self.api_key:
            self._initialize_client()

    def _initialize_client(self):
        try:
            if genai is None:
                logger.error("Install new SDK: pip install google-genai")
                return False

            self.client = genai.Client(api_key=self.api_key)

            logger.info("LLM client initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return False

    def is_available(self) -> bool:
        return self.client is not None

    def test_connection(self) -> Dict[str, Any]:
        """Test LLM API connection with a simple request."""
        log_operation_start(logger, "LLM connection test")

        if not self.is_available():
            return {
                "success": False,
                "error": "LLM service not available - check API key"
            }

        try:
            start_time = time.time()

            prompt = PromptService.create_test_prompt()
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            processing_time = int((time.time() - start_time) * 1000)

            log_operation_end(
                logger,
                "LLM connection test",
                True,
                f"Completed in {processing_time}ms"
            )

            return {
                "success": True,
                "response": response.text,
                "processing_time": processing_time,
                "model": self.model_name,
                "timestamp": time.time()
            }

        except Exception as e:
            log_operation_end(logger, "LLM connection test", False, str(e))
            return {
                "success": False,
                "error": f"API test failed: {str(e)}"
            }
  


    def process_faculty_extraction(self, raw_data: str) -> Dict[str, Any]:
        """Extract faculty information from raw data."""
        log_operation_start(logger, "Faculty extraction", "Extracting faculty with LLM")
        
        if not self.is_available():
            return {
                "success": False,
                "error": "LLM service not available",
                "processing_type": "faculty_extraction"
            }
        
        try:
            start_time = time.time()
            
            prompt = PromptService.create_college_faculty_extraction_prompt(raw_data)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            processed_data = self._parse_llm_response(response.text, "faculty_extraction")
            
            log_operation_end(logger, "Faculty extraction", True, f"Completed in {processing_time}ms")
            
            return {
                "success": True,
                "processing_type": "faculty_extraction",
                "raw_data": raw_data,
                "processed_data": processed_data,
                "processing_time": processing_time,
                "model": self.model_name,
                "timestamp": time.time()
            }
            
        except Exception as e:
            log_operation_end(logger, "Faculty extraction", False, str(e))
            return {
                "success": False,
                "error": f"Faculty extraction failed: {str(e)}",
                "processing_type": "faculty_extraction"
            }
    
    def _parse_llm_response(self, response_text: str, processing_type: str) -> Dict[str, Any]:
        """Parse LLM response and handle JSON parsing."""
        try:
            # Clean response text - remove markdown code blocks
            cleaned_text = response_text.strip()
            
            # Remove markdown code block markers
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]   # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove ```
            
            cleaned_text = cleaned_text.strip()
            
            data = json.loads(cleaned_text)
            logger.info(f"Successfully parsed {processing_type} response")
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse {processing_type} as JSON, returning raw text. Error: {str(e)}")
            return {
                "processing_type": processing_type,
                "raw_response": response_text,
                "parsing_error": "Failed to parse JSON response"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM service status."""
        return {
            "available": self.is_available(),
            "model": self.model_name,
            "api_key_configured": bool(self.api_key),
            "client_initialized": self.client is not None,
            "library_version": genai.__version__ if genai else None
        }