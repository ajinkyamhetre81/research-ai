"""
Response schemas for document processing operations.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class FileInfo(BaseModel):
    """File information schema."""
    filename: str
    file_size: int
    mime_type: str
    extension: str


class ExtractionSummary(BaseModel):
    """Text extraction summary schema."""
    total_pages: int
    pages_with_content: int
    total_words_extracted: int
    extraction_method: str
    avg_words_per_page: float


class PageData(BaseModel):
    """Individual page data schema."""
    page: int
    text: str
    char_count: int
    word_count: int
    has_content: bool
    extraction_method: str
    languages_detected: List[str]


class ValidationErrorDetail(BaseModel):
    """Validation error details schema."""
    filename: str
    provided_extension: str
    allowed_extensions: List[str]
    suggestion: str


class ErrorDetail(BaseModel):
    """General error detail schema."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None


class PDFUploadSuccessResponse(BaseModel):
    """Successful PDF upload response schema."""
    success: bool = True
    message: str
    file_info: FileInfo
    extraction_summary: ExtractionSummary
    pages_data: List[PageData]
    timestamp: datetime
    processing_time_ms: Optional[float] = None


class PDFUploadErrorResponse(BaseModel):
    """PDF upload error response schema."""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime


class InvalidExtensionErrorResponse(BaseModel):
    """Invalid file extension error response."""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    """PDF validation error response."""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime


class ProcessingErrorResponse(BaseModel):
    """Processing error response."""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str
    service: str
    timestamp: datetime
    version: str = "1.0.0"


class DocumentAnalysisRequest(BaseModel):
    """Document analysis request schema."""
    document_id: Optional[str] = None
    analysis_type: str = "full"
    options: Optional[Dict[str, Any]] = None


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response schema."""
    success: bool
    message: str
    analysis_results: Optional[Dict[str, Any]] = None
    timestamp: datetime


class PDFURLRequest(BaseModel):
    """PDF URL processing request schema."""
    pdf_url: str
    languages: List[str] = ["eng"]
    options: Optional[Dict[str, Any]] = None
    page_range: Optional[str] = None
    """
    Page range format examples:
    - "1" (single page)
    - "1,3,5" (specific pages)
    - "1-5" (range from page 1 to 5)
    - "1-3,5,7-9" (combination of ranges and specific pages)
    """


class PDFURLResponse(BaseModel):
    """PDF URL processing response schema."""
    success: bool
    message: str
    source: str  # "url" or "upload"
    file_info: Optional[FileInfo] = None
    extraction_summary: Optional[ExtractionSummary] = None
    pages_data: Optional[List[PageData]] = None
    timestamp: datetime
    processing_time_ms: Optional[float] = None


# Response type aliases for easier usage
PDFUploadResponse = Union[PDFUploadSuccessResponse, PDFUploadErrorResponse, InvalidExtensionErrorResponse, ValidationErrorResponse, ProcessingErrorResponse]
DocumentResponse = Union[DocumentAnalysisResponse, PDFUploadErrorResponse, ProcessingErrorResponse]
PDFProcessResponse = Union[PDFURLResponse, PDFUploadErrorResponse, ProcessingErrorResponse]
