"""
Google Cloud Storage integration for Vectorpenter
Archive raw, translated, and redacted text artifacts for audits
"""

from __future__ import annotations
from typing import Optional, Dict, Any
import time
import json
from pathlib import Path
from core.config import settings
from core.logging import logger

# Global client for reuse
_client = None

def _client_init():
    """Initialize GCS client (lazy loading)"""
    global _client
    if _client is None:
        try:
            from google.cloud import storage
            _client = storage.Client()
            logger.debug("GCS client initialized")
        except ImportError:
            raise ImportError("Google Cloud Storage libraries not installed")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GCS client: {e}")
    return _client


def upload_bytes(name: str, data: bytes, content_type: str = "text/plain") -> str:
    """
    Upload bytes to Google Cloud Storage
    
    Args:
        name: File name for the upload
        data: Bytes to upload
        content_type: MIME type of the content
        
    Returns:
        GCS URI (gs://bucket/path) or empty string on failure
    """
    try:
        if not settings.gcs_bucket:
            logger.warning("GCS_BUCKET not configured")
            return ""
        
        client = _client_init()
        
        # Clean bucket name (remove gs:// prefix if present)
        bucket_name = settings.gcs_bucket.replace("gs://", "")
        
        # Create blob path with timestamp and prefix
        prefix = settings.gcs_prefix.rstrip("/")
        timestamp = int(time.time() * 1000)  # millisecond precision
        blob_path = f"{prefix}/{timestamp}_{name}"
        
        # Get bucket and create blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        logger.debug(f"Uploading to GCS: {len(data)} bytes -> gs://{bucket_name}/{blob_path}")
        
        # Upload data
        blob.upload_from_string(data, content_type=content_type)
        
        # Return full GCS URI
        gcs_uri = f"gs://{bucket_name}/{blob_path}"
        logger.info(f"GCS upload successful: {gcs_uri}")
        
        return gcs_uri
        
    except Exception as e:
        logger.warning(f"GCS upload failed: {e}")
        return ""


def upload_text(name: str, text: str) -> str:
    """
    Upload text content to GCS
    
    Args:
        name: File name for the upload
        text: Text content to upload
        
    Returns:
        GCS URI or empty string on failure
    """
    return upload_bytes(name, text.encode('utf-8'), content_type="text/plain")


def upload_json(name: str, data: Dict[Any, Any]) -> str:
    """
    Upload JSON data to GCS
    
    Args:
        name: File name for the upload
        data: Dictionary to upload as JSON
        
    Returns:
        GCS URI or empty string on failure
    """
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
    return upload_bytes(name, json_bytes, content_type="application/json")


def archive_document_artifacts(
    document_path: str,
    raw_text: str,
    translated_text: Optional[str] = None,
    redacted_text: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Archive document processing artifacts to GCS
    
    Args:
        document_path: Original document path
        raw_text: Raw extracted text
        translated_text: Translated text (if translation was applied)
        redacted_text: Redacted text (if DLP was applied)
        metadata: Additional metadata to store
        
    Returns:
        Dictionary mapping artifact type to GCS URI
    """
    if not settings.use_gcs:
        return {}
    
    try:
        # Create base name from document path
        doc_name = Path(document_path).stem
        uris = {}
        
        # Upload raw text
        if raw_text:
            raw_name = f"{doc_name}.raw.txt"
            raw_uri = upload_text(raw_name, raw_text)
            if raw_uri:
                uris["raw"] = raw_uri
        
        # Upload translated text
        if translated_text and translated_text != raw_text:
            translated_name = f"{doc_name}.translated.txt"
            translated_uri = upload_text(translated_name, translated_text)
            if translated_uri:
                uris["translated"] = translated_uri
        
        # Upload redacted text
        if redacted_text and redacted_text != (translated_text or raw_text):
            redacted_name = f"{doc_name}.redacted.txt"
            redacted_uri = upload_text(redacted_name, redacted_text)
            if redacted_uri:
                uris["redacted"] = redacted_uri
        
        # Upload metadata
        if metadata:
            metadata_name = f"{doc_name}.metadata.json"
            metadata_uri = upload_json(metadata_name, metadata)
            if metadata_uri:
                uris["metadata"] = metadata_uri
        
        if uris:
            logger.info(f"Archived {len(uris)} artifacts for {doc_name}: {list(uris.keys())}")
        
        return uris
        
    except Exception as e:
        logger.warning(f"Failed to archive artifacts for {document_path}: {e}")
        return {}


def is_gcs_available() -> bool:
    """
    Check if Google Cloud Storage is available and properly configured
    
    Returns:
        True if GCS can be used, False otherwise
    """
    try:
        # Check if libraries are installed
        from google.cloud import storage
        
        # Check configuration
        if not all([
            settings.gcs_bucket,
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
        logger.debug("Google Cloud Storage libraries not installed")
        return False
    except Exception as e:
        logger.warning(f"GCS availability check failed: {e}")
        return False


def test_gcs_connection() -> bool:
    """
    Test Google Cloud Storage connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        if not is_gcs_available():
            logger.warning("GCS not properly configured")
            return False
        
        client = _client_init()
        bucket_name = settings.gcs_bucket.replace("gs://", "")
        
        # Try to access the bucket
        bucket = client.bucket(bucket_name)
        
        # Test with a simple operation (check if bucket exists)
        bucket.reload()
        
        logger.info(f"GCS connection successful: {bucket_name}")
        return True
        
    except Exception as e:
        logger.warning(f"GCS connection test failed: {e}")
        return False


def estimate_gcs_cost(data_size_bytes: int, operations_count: int = 1) -> dict:
    """
    Estimate Google Cloud Storage cost
    
    Args:
        data_size_bytes: Size of data to store in bytes
        operations_count: Number of operations (uploads)
        
    Returns:
        Dictionary with cost estimates
    """
    # GCS pricing (as of 2025) - Standard storage
    # Storage: $0.020 per GB per month
    # Operations: $0.05 per 10,000 Class A operations (uploads)
    
    storage_cost_per_gb_month = 0.020
    operations_cost_per_10k = 0.05
    
    data_size_gb = data_size_bytes / (1024**3)
    monthly_storage_cost = data_size_gb * storage_cost_per_gb_month
    operations_cost = (operations_count / 10_000) * operations_cost_per_10k
    
    return {
        "data_size_gb": round(data_size_gb, 6),
        "monthly_storage_cost_usd": round(monthly_storage_cost, 6),
        "operations_cost_usd": round(operations_cost, 6),
        "operations_count": operations_count,
        "note": "Estimates based on Standard storage pricing"
    }


def list_archived_documents(limit: int = 100) -> List[Dict[str, Any]]:
    """
    List recently archived documents
    
    Args:
        limit: Maximum number of documents to return
        
    Returns:
        List of document information
    """
    try:
        if not is_gcs_available():
            return []
        
        client = _client_init()
        bucket_name = settings.gcs_bucket.replace("gs://", "")
        bucket = client.bucket(bucket_name)
        
        # List blobs with the configured prefix
        blobs = bucket.list_blobs(prefix=settings.gcs_prefix, max_results=limit)
        
        documents = []
        for blob in blobs:
            documents.append({
                "name": blob.name,
                "size_bytes": blob.size,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "content_type": blob.content_type,
                "uri": f"gs://{bucket_name}/{blob.name}"
            })
        
        return documents
        
    except Exception as e:
        logger.warning(f"Failed to list archived documents: {e}")
        return []


def cleanup_old_archives(days_old: int = 30) -> int:
    """
    Clean up old archived documents
    
    Args:
        days_old: Delete archives older than this many days
        
    Returns:
        Number of files deleted
    """
    try:
        if not is_gcs_available():
            return 0
        
        client = _client_init()
        bucket_name = settings.gcs_bucket.replace("gs://", "")
        bucket = client.bucket(bucket_name)
        
        # Calculate cutoff time
        import datetime
        cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_old)
        
        # List and delete old blobs
        blobs = bucket.list_blobs(prefix=settings.gcs_prefix)
        deleted_count = 0
        
        for blob in blobs:
            if blob.time_created and blob.time_created < cutoff_time:
                blob.delete()
                deleted_count += 1
                logger.debug(f"Deleted old archive: {blob.name}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old archives (older than {days_old} days)")
        
        return deleted_count
        
    except Exception as e:
        logger.warning(f"Archive cleanup failed: {e}")
        return 0
