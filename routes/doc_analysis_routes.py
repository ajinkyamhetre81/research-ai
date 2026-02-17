from fastapi import APIRouter, UploadFile, HTTPException
from typing import Optional
from services.document_processor_services import PDFDocumentProcessor
from utils.loggers import get_logger, log_with_context, log_operation_start, log_operation_end
from schemas.document_schemas import (
    PDFUploadSuccessResponse, PDFUploadErrorResponse, InvalidExtensionErrorResponse,
    ValidationErrorResponse, ProcessingErrorResponse, FileInfo, ExtractionSummary,
    PageData, ErrorDetail, ValidationErrorDetail, PDFUploadResponse,
    PDFURLRequest, PDFURLResponse, PDFProcessResponse
)
import os
from datetime import datetime
import time

router = APIRouter()
logger = get_logger(__name__)

# Initialize PDF processor
pdf_processor = PDFDocumentProcessor()


@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(upload_file: UploadFile, page_range: Optional[str] = None):
    """Upload and process a PDF file."""
    
    start_time = time.time()
    log_operation_start(logger, "PDF upload", f"processing file: {upload_file.filename}")
    
    try:
        # Basic validation
        if not upload_file.filename:
            log_operation_end(logger, "PDF upload", False, "no filename provided")
            raise HTTPException(
                status_code=400,
                detail=PDFUploadErrorResponse(
                    error=ErrorDetail(
                        error_code="no_filename",
                        message="No filename provided",
                        suggestion="Please provide a filename when uploading"
                    ),
                    timestamp=datetime.now()
                ).dict()
            )
        
        file_extension = os.path.splitext(upload_file.filename)[1].lower()
        
        # Check file extension
        if file_extension != '.pdf':
            log_with_context(
                logger,
                f"Invalid file extension: {file_extension}",
                level="WARNING",
                extra_context={
                    "filename": upload_file.filename,
                    "extension": file_extension,
                    "allowed": ".pdf"
                }
            )
            
            log_operation_end(logger, "PDF upload", False, f"invalid extension: {file_extension}")
            
            raise HTTPException(
                status_code=400,
                detail=InvalidExtensionErrorResponse(
                    error=ErrorDetail(
                        error_code="invalid_extension",
                        message=f"File extension '{file_extension}' not allowed. Only PDF files accepted.",
                        details=ValidationErrorDetail(
                            filename=upload_file.filename,
                            provided_extension=file_extension,
                            allowed_extensions=['.pdf'],
                            suggestion="Please upload a PDF file"
                        ).dict()
                    ),
                    timestamp=datetime.now()
                ).dict()
            )
        
        # Validate the PDF
        log_with_context(
            logger,
            f"Validating PDF: {upload_file.filename}",
            level="INFO",
            extra_context={
                "content_type": upload_file.content_type,
                "file_size": getattr(upload_file, 'size', 'unknown'),
                "extension": file_extension
            }
        )
        
        validation_result = pdf_processor.validate(upload_file)
        
        if not validation_result["is_valid"]:
            log_operation_end(logger, "PDF upload", False, "validation failed")
            raise HTTPException(
                status_code=400,
                detail=ValidationErrorResponse(
                    error=ErrorDetail(
                        error_code="validation_failed",
                        message=validation_result.get('message', 'Validation failed'),
                        details=validation_result
                    ),
                    timestamp=datetime.now()
                ).dict()
            )
        
        # Extract text
        log_with_context(
            logger,
            "Extracting text from PDF",
            level="INFO",
            extra_context={
                "filename": validation_result["filename"],
                "file_size": validation_result["file_size"],
                "page_range": page_range or "all"
            }
        )
        
        extracted_pages = await pdf_processor.extract_text(upload_file, languages=['eng'], page_range=page_range)
        
        # Calculate stats
        total_pages = len(extracted_pages)
        pages_with_content = sum(1 for page in extracted_pages if page["has_content"])
        total_words = sum(page["word_count"] for page in extracted_pages)
        processing_time = (time.time() - start_time) * 1000
        
        # Build response
        response = PDFUploadSuccessResponse(
            success=True,
            message="PDF processed successfully",
            file_info=FileInfo(
                filename=validation_result["filename"],
                file_size=validation_result["file_size"],
                mime_type=validation_result["mime_type"],
                extension=file_extension
            ),
            extraction_summary=ExtractionSummary(
                total_pages=total_pages,
                pages_with_content=pages_with_content,
                total_words_extracted=total_words,
                extraction_method="PyMuPDF",
                avg_words_per_page=total_words / total_pages if total_pages > 0 else 0
            ),
            pages_data=[PageData(**page) for page in extracted_pages],
            timestamp=datetime.now(),
            processing_time_ms=processing_time
        )
        
        log_operation_end(logger, "PDF upload", True, 
                      f"processed {total_pages} pages, {total_words} words")
        
        return response.dict()
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        log_operation_end(
            logger,
            "PDF upload",
            False,
            f"unexpected error: {str(e)}"
        )
        
        logger.error(f"PDF upload failed with unexpected error: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail=ProcessingErrorResponse(
                error=ErrorDetail(
                    error_code="processing_error",
                    message=f"Internal server error during PDF processing: {str(e)}",
                    suggestion="Please try again later or contact support if the issue persists"
                ),
                timestamp=datetime.now()
            ).dict()
        )



@router.post("/process-pdf-url", response_model=PDFProcessResponse)
async def process_pdf_url(request: PDFURLRequest):
    """Process PDF from URL."""
    
    start_time = time.time()
    log_operation_start(logger, "PDF URL processing", f"processing URL: {request.pdf_url}")
    
    try:
        # Validate URL
        if not request.pdf_url or not request.pdf_url.strip():
            log_operation_end(logger, "PDF URL processing", False, "empty URL")
            raise HTTPException(
                status_code=400,
                detail=PDFUploadErrorResponse(
                    error=ErrorDetail(
                        error_code="empty_url",
                        message="PDF URL is required",
                        suggestion="Please provide a valid PDF URL"
                    ),
                    timestamp=datetime.now()
                ).dict()
            )
        
        # Process PDF from URL
        extracted_pages = await pdf_processor.extract_text(
            request.pdf_url, 
            languages=request.languages,
            page_range=request.page_range
        )
        
        # Calculate stats
        total_pages = len(extracted_pages)
        pages_with_content = sum(1 for page in extracted_pages if page["has_content"])
        total_words = sum(page["word_count"] for page in extracted_pages)
        processing_time = (time.time() - start_time) * 1000
        
        # Build response
        response = PDFURLResponse(
            success=True,
            message="PDF processed successfully from URL",
            source="url",
            extraction_summary=ExtractionSummary(
                total_pages=total_pages,
                pages_with_content=pages_with_content,
                total_words_extracted=total_words,
                extraction_method="PyMuPDF",
                avg_words_per_page=total_words / total_pages if total_pages > 0 else 0
            ),
            pages_data=[PageData(**page) for page in extracted_pages],
            timestamp=datetime.now(),
            processing_time_ms=processing_time
        )
        
        log_operation_end(logger, "PDF URL processing", True, 
                      f"processed {total_pages} pages, {total_words} words")
        
        return response.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        log_operation_end(logger, "PDF URL processing", False, f"error: {str(e)}")
        logger.error(f"PDF URL processing failed: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail=ProcessingErrorResponse(
                error=ErrorDetail(
                    error_code="url_processing_error",
                    message=f"Failed to process PDF from URL: {str(e)}",
                    suggestion="Please check the URL and try again"
                ),
                timestamp=datetime.now()
            ).dict()
        )






