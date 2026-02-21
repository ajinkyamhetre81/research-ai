# services/llm_service.py

import os
import time
from typing import Dict, Any, Optional
from utils.loggers import get_logger, log_operation_start, log_operation_end

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

            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello! Please respond with 'API connection successful!'"
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM service status."""
        return {
            "available": self.is_available(),
            "model": self.model_name,
            "api_key_configured": bool(self.api_key),
            "client_initialized": self.client is not None,
            "library_version": genai.__version__ if genai else None
        }