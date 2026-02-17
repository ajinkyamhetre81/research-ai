from abc import ABC, abstractmethod
from fastapi import UploadFile
import logging
import os
import json
import tempfile
import requests
import io
from urllib.parse import urlparse
from utils.loggers import get_logger, log_with_context, log_operation_start, log_operation_end


class DocumentProcessorServices(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def process(self, document):
        pass




class PDFDocumentProcessor(DocumentProcessorServices):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_mime_types = ['application/pdf']
        self.allowed_extensions = ['.pdf']
        
        # Try to import PyMuPDF (most accurate)
        try:
            import fitz
            self.fitz = fitz
            self.use_ocr = False
            self.logger.info("PyMuPDF (fitz) loaded successfully - using direct text extraction")
        except ImportError:
            self.logger.warning("PyMuPDF not available, would need OCR fallback")
            self.fitz = None
            self.use_ocr = True
        
        # Try to import OCR dependencies
        try:
            import pytesseract
            from PIL import Image
            self.ocr_available = True
            self.pytesseract = pytesseract
            self.Image = Image
            self.logger.info("OCR dependencies (pytesseract, Pillow) loaded successfully")
        except ImportError:
            self.ocr_available = False
            self.logger.warning("OCR dependencies not available - scanned PDFs will not be processed")

    def validate(self, upload_file: UploadFile):
        """
        Validate uploaded PDF file.
        
        Args:
            upload_file: FastAPI UploadFile object
            
        Returns:
            dict: Validation result with is_valid boolean and message
            
        Raises:
            ValueError: If file is invalid
        """
        self.logger.info(f"Starting PDF validation for file: {upload_file.filename}")
        
        validation_errors = []
        
        # Check if filename is provided
        if not upload_file.filename:
            error_msg = "No filename provided"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check file extension
        file_extension = os.path.splitext(upload_file.filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            error_msg = f"Invalid file extension: {file_extension}. Allowed: {self.allowed_extensions}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check MIME type
        if upload_file.content_type not in self.allowed_mime_types:
            error_msg = f"Invalid MIME type: {upload_file.content_type}. Allowed: {self.allowed_mime_types}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check file size
        try:
            # Reset file pointer to start
            upload_file.file.seek(0, 2)  # Seek to end
            file_size = upload_file.file.tell()
            upload_file.file.seek(0)  # Reset to start
            
            if file_size > self.max_file_size:
                error_msg = f"File too large: {file_size} bytes. Max allowed: {self.max_file_size} bytes"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            if file_size == 0:
                error_msg = "File is empty"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"Error checking file size: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check PDF file signature (magic numbers)
        try:
            # Read first few bytes to check PDF signature
            current_pos = upload_file.file.tell()
            upload_file.file.seek(0)
            file_header = upload_file.file.read(5)
            upload_file.file.seek(current_pos)  # Reset to original position
            
            if not file_header.startswith(b'%PDF-'):
                error_msg = "File does not have valid PDF signature"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"Error reading file header: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log successful validation
        from utils.loggers import log_with_context
        log_with_context(
            self.logger,
            f"PDF validation successful for {upload_file.filename}",
            level="INFO",
            extra_context={
                "file_size": file_size,
                "mime_type": upload_file.content_type,
                "extension": file_extension
            }
        )
        
        return {
            "is_valid": True,
            "filename": upload_file.filename,
            "file_size": file_size,
            "mime_type": upload_file.content_type,
            "message": "PDF file is valid"
        }

    def _parse_page_range(self, page_range: str, total_pages: int):
        """
        Parse page range string into list of page numbers.
        
        Args:
            page_range: Page range string (e.g., "1", "1,3,5", "1-5", "1-3,5,7-9")
            total_pages: Total number of pages in PDF
            
        Returns:
            list: List of page numbers to extract
        """
        if not page_range:
            return list(range(1, total_pages + 1))
        
        pages = set()
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle range (e.g., "1-5")
                start, end = part.split('-', 1)
                try:
                    start_page = int(start.strip())
                    end_page = int(end.strip())
                    if start_page < 1 or end_page > total_pages or start_page > end_page:
                        continue
                    pages.update(range(start_page, end_page + 1))
                except ValueError:
                    continue
            else:
                # Handle single page (e.g., "1")
                try:
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        pages.add(page_num)
                except ValueError:
                    continue
        
        return sorted(list(pages))

    async def extract_text(self, document, languages=['eng'], page_range=None):
        """
        Extract text from PDF document page-wise using PyMuPDF (most accurate).
        
        Args:
            document: PDF file path, file-like object, or URL string
            languages: List of language codes for OCR fallback (if needed)
            page_range: Page range string (e.g., "1", "1,3,5", "1-5", "1-3,5,7-9")
            
        Returns:
            list: JSON-compatible list with page-wise text extraction
        """
        log_operation_start(self.logger, "PDF text extraction", f"processing document: {document}")
        
        try:
            # Handle different input types
            if isinstance(document, str) and document.startswith(('http://', 'https://')):
                # Handle URL input
                self.logger.info(f"Downloading PDF from URL: {document}")
                
                # Download PDF from URL
                response = requests.get(document, timeout=30)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
                
                doc = self.fitz.open(temp_file_path)
                cleanup_temp = True
                source_type = "url"
                
            elif hasattr(document, 'read'):
                # Handle file-like object (UploadFile)
                await document.seek(0)
                content = await document.read()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                doc = self.fitz.open(temp_file_path)
                cleanup_temp = True
                source_type = "upload"
                
            else:
                # Handle file path
                doc = self.fitz.open(document)
                cleanup_temp = False
                source_type = "local"
            
            pages_data = []
            total_pages = len(doc)
            
            # Parse page range
            pages_to_extract = self._parse_page_range(page_range, total_pages)
            
            log_with_context(
                self.logger,
                f"Starting text extraction from {len(pages_to_extract)} pages (total: {total_pages})",
                level="INFO",
                extra_context={
                    "total_pages": total_pages,
                    "pages_to_extract": len(pages_to_extract),
                    "page_range": page_range or "all",
                    "extraction_method": "PyMuPDF",
                    "languages": languages,
                    "source_type": source_type
                }
            )
            
            for page_num in pages_to_extract:
                page = doc[page_num - 1]  # Convert to 0-based index
                
                # Extract text using PyMuPDF (most accurate method)
                text = page.get_text()
                
                # If no text found, try OCR
                if not text.strip():
                    log_with_context(
                        self.logger,
                        f"No text found on page {page_num + 1}, attempting OCR",
                        level="INFO",
                        extra_context={"page": page_num + 1}
                    )
                    
                    if self.ocr_available:
                        try:
                            # Convert page to image
                            pix = page.get_pixmap()
                            img_data = pix.tobytes("png")
                            image = self.Image.open(io.BytesIO(img_data))
                            
                            # Perform OCR
                            lang_code = languages[0] if languages else 'eng'
                            ocr_text = self.pytesseract.image_to_string(image, lang=lang_code)
                            
                            if ocr_text.strip():
                                text = ocr_text
                                log_with_context(
                                    self.logger,
                                    f"OCR successful on page {page_num + 1}",
                                    level="INFO",
                                    extra_context={
                                        "page": page_num + 1,
                                        "ocr_language": lang_code,
                                        "char_count": len(ocr_text)
                                    }
                                )
                            else:
                                text = "[OCR_FAILED: No text detected in image]"
                                log_with_context(
                                    self.logger,
                                    f"OCR failed on page {page_num + 1} - no text detected",
                                    level="WARNING",
                                    extra_context={"page": page_num + 1}
                                )
                                
                        except Exception as ocr_error:
                            text = f"[OCR_ERROR: {str(ocr_error)}]"
                            log_with_context(
                                self.logger,
                                f"OCR error on page {page_num + 1}",
                                level="ERROR",
                                extra_context={
                                    "page": page_num + 1,
                                    "error": str(ocr_error)
                                }
                            )
                    else:
                        text = "[OCR_UNAVAILABLE: Install pytesseract and Pillow for scanned PDF support]"
                        log_with_context(
                            self.logger,
                            f"OCR not available for page {page_num + 1}",
                            level="WARNING",
                            extra_context={"page": page_num + 1}
                        )
                
                # Determine extraction method
                extraction_method = "PyMuPDF"
                if not text.strip() or "[OCR_" in text:
                    extraction_method = "OCR"
                
                # Create page data structure
                page_data = {
                    "page": page_num + 1,
                    "text": text.strip(),
                    "char_count": len(text),
                    "word_count": len(text.split()) if text.strip() else 0,
                    "has_content": bool(text.strip()),
                    "extraction_method": extraction_method,
                    "languages_detected": languages
                }
                
                pages_data.append(page_data)
                
                log_with_context(
                    self.logger,
                    f"Extracted text from page {page_num + 1}",
                    level="DEBUG",
                    extra_context={
                        "page": page_num + 1,
                        "char_count": page_data["char_count"],
                        "word_count": page_data["word_count"]
                    }
                )
            
            # Close document
            doc.close()
            
            # Clean up temporary file if created
            if cleanup_temp and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            # Calculate summary statistics
            total_chars = sum(page["char_count"] for page in pages_data)
            total_words = sum(page["word_count"] for page in pages_data)
            pages_with_content = sum(1 for page in pages_data if page["has_content"])
            
            log_operation_end(
                self.logger,
                "PDF text extraction",
                True,
                f"extracted {total_words} words from {pages_with_content}/{total_pages} pages"
            )
            
            log_with_context(
                self.logger,
                "Text extraction summary",
                level="INFO",
                extra_context={
                    "total_pages": total_pages,
                    "pages_with_content": pages_with_content,
                    "total_characters": total_chars,
                    "total_words": total_words,
                    "avg_words_per_page": total_words / total_pages if total_pages > 0 else 0,
                    "source_type": source_type
                }
            )
            
            return pages_data
            
        except Exception as e:
            log_operation_end(
                self.logger,
                "PDF text extraction",
                False,
                f"error: {str(e)}"
            )
            self.logger.error(f"Text extraction failed: {str(e)}", exc_info=True)
            raise


    def process(self, document):
        pass
    

