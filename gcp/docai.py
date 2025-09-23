"""
Google Cloud Document AI integration for Vectorpenter
Auto-upgrade PDF parsing when local extraction yields poor results
"""

from __future__ import annotations
from pathlib import Path
from typing import Tuple
from core.config import settings
from core.logging import logger

def parse_pdf_with_docai(path: Path) -> Tuple[str, dict]:
    """
    Parse PDF using Google Cloud Document AI
    
    Args:
        path: Path to PDF file
        
    Returns:
        Tuple of (extracted_text, metadata)
        Returns empty text and error metadata on failure
    """
    try:
        # Import GCP libraries (optional dependency)
        from google.cloud import documentai
        from google.api_core import exceptions as gcp_exceptions
        
        # Validate configuration
        if not settings.gcp_project_id:
            error_msg = "GCP_PROJECT_ID not configured"
            logger.warning(f"DocAI parsing failed: {error_msg}")
            return "", {"source": str(path), "parser": "docai_error", "error": error_msg}
        
        if not settings.doc_ai_processor_id:
            error_msg = "DOC_AI_PROCESSOR_ID not configured"
            logger.warning(f"DocAI parsing failed: {error_msg}")
            return "", {"source": str(path), "parser": "docai_error", "error": error_msg}
        
        # Initialize Document AI client
        client = documentai.DocumentProcessorServiceClient()
        
        # Read file bytes
        with open(path, "rb") as file:
            file_content = file.read()
        
        # Prepare document for processing
        raw_document = documentai.RawDocument(
            content=file_content,
            mime_type="application/pdf"
        )
        
        # Configure the process request
        request = documentai.ProcessRequest(
            name=settings.doc_ai_processor_id,
            raw_document=raw_document
        )
        
        logger.info(f"Sending PDF to Document AI: {path.name} ({len(file_content)} bytes)")
        
        # Process document
        result = client.process_document(request=request)
        document = result.document
        
        # Extract text from all pages
        page_texts = []
        for page in document.pages:
            page_text = ""
            
            # Extract paragraphs
            for paragraph in page.paragraphs:
                paragraph_text = ""
                for segment in paragraph.layout.text_anchor.text_segments:
                    start_index = int(segment.start_index) if segment.start_index else 0
                    end_index = int(segment.end_index) if segment.end_index else len(document.text)
                    paragraph_text += document.text[start_index:end_index]
                page_text += paragraph_text + "\n"
            
            # If no paragraphs found, use raw page text
            if not page_text.strip() and hasattr(page, 'layout') and page.layout.text_anchor:
                for segment in page.layout.text_anchor.text_segments:
                    start_index = int(segment.start_index) if segment.start_index else 0
                    end_index = int(segment.end_index) if segment.end_index else len(document.text)
                    page_text += document.text[start_index:end_index]
            
            if page_text.strip():
                page_texts.append(page_text.strip())
        
        # Join all pages with newlines
        extracted_text = "\n\n".join(page_texts)
        
        # Create metadata
        metadata = {
            "source": str(path),
            "parser": "docai",
            "pages_processed": len(document.pages),
            "total_characters": len(extracted_text),
            "processor_id": settings.doc_ai_processor_id
        }
        
        logger.info(f"DocAI extraction completed: {path.name} -> {len(extracted_text)} characters from {len(document.pages)} pages")
        
        return extracted_text, metadata
        
    except ImportError as e:
        error_msg = f"Google Cloud libraries not installed: {e}"
        logger.warning(f"DocAI parsing failed: {error_msg}")
        return "", {"source": str(path), "parser": "docai_error", "error": error_msg}
    
    except gcp_exceptions.GoogleAPICallError as e:
        error_msg = f"Document AI API error: {e}"
        logger.error(f"DocAI parsing failed: {error_msg}")
        return "", {"source": str(path), "parser": "docai_error", "error": error_msg}
    
    except gcp_exceptions.PermissionDenied as e:
        error_msg = f"Permission denied for Document AI: {e}"
        logger.error(f"DocAI parsing failed: {error_msg}")
        return "", {"source": str(path), "parser": "docai_error", "error": error_msg}
    
    except FileNotFoundError as e:
        error_msg = f"File not found: {e}"
        logger.error(f"DocAI parsing failed: {error_msg}")
        return "", {"source": str(path), "parser": "docai_error", "error": error_msg}
    
    except Exception as e:
        error_msg = f"Unexpected DocAI error: {e}"
        logger.error(f"DocAI parsing failed: {error_msg}")
        return "", {"source": str(path), "parser": "docai_error", "error": error_msg}


def is_docai_available() -> bool:
    """
    Check if Document AI is available and properly configured
    
    Returns:
        True if DocAI can be used, False otherwise
    """
    try:
        # Check if GCP libraries are installed
        from google.cloud import documentai
        
        # Check if configuration is complete
        if not all([
            settings.gcp_project_id,
            settings.doc_ai_processor_id,
            settings.google_application_credentials
        ]):
            return False
        
        # Check if credentials file exists
        if settings.google_application_credentials:
            creds_path = Path(settings.google_application_credentials)
            if not creds_path.exists():
                logger.warning(f"Google credentials file not found: {creds_path}")
                return False
        
        return True
        
    except ImportError:
        logger.debug("Google Cloud libraries not installed, DocAI unavailable")
        return False
    except Exception as e:
        logger.warning(f"DocAI availability check failed: {e}")
        return False


def get_docai_usage_estimate(file_size_bytes: int) -> dict:
    """
    Estimate Document AI usage and cost for a file
    
    Args:
        file_size_bytes: Size of the file in bytes
        
    Returns:
        Dictionary with usage estimates
    """
    # Rough estimates based on Google's pricing
    # Document AI pricing is per page, estimate ~100KB per page for PDFs
    estimated_pages = max(1, file_size_bytes // (100 * 1024))
    
    # Pricing estimates (as of 2025) - these are approximate
    cost_per_page = 0.015  # $0.015 per page for Document OCR
    estimated_cost = estimated_pages * cost_per_page
    
    return {
        "estimated_pages": estimated_pages,
        "estimated_cost_usd": round(estimated_cost, 4),
        "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
        "note": "Estimates based on ~100KB per page and $0.015/page pricing"
    }


def test_docai_connection() -> bool:
    """
    Test Document AI connection and configuration
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from google.cloud import documentai
        
        if not is_docai_available():
            logger.warning("DocAI not properly configured")
            return False
        
        # Try to initialize client
        client = documentai.DocumentProcessorServiceClient()
        
        # Try to get processor info (this validates credentials and processor ID)
        processor_name = settings.doc_ai_processor_id
        processor = client.get_processor(name=processor_name)
        
        logger.info(f"DocAI connection successful: {processor.display_name} ({processor.type_})")
        return True
        
    except ImportError:
        logger.warning("Google Cloud libraries not installed")
        return False
    except Exception as e:
        logger.warning(f"DocAI connection test failed: {e}")
        return False
