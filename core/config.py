from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # LLM and embedding APIs
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    voyage_api_key: str | None = os.getenv("VOYAGE_API_KEY")
    
    # Vector database (Pinecone)
    pinecone_api_key: str | None = os.getenv("PINECONE_API_KEY")
    pinecone_index: str = os.getenv("PINECONE_INDEX", "vectorpenter")
    pinecone_cloud: str = os.getenv("PINECONE_CLOUD", "gcp")
    pinecone_region: str = os.getenv("PINECONE_REGION", "us-central1")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "default")
    
    # Local state database
    db_url: str = os.getenv("DB_URL", "sqlite:///./data/vectorpenter.db")
    
    # Typesense (keyword search)
    typesense_api_key: str | None = os.getenv("TYPESENSE_API_KEY")
    typesense_host: str = os.getenv("TYPESENSE_HOST", "localhost")
    typesense_port: int = int(os.getenv("TYPESENSE_PORT", "8108"))
    typesense_protocol: str = os.getenv("TYPESENSE_PROTOCOL", "http")
    typesense_collection: str = os.getenv("TYPESENSE_COLLECTION", "vectorpenter_chunks")
    
    # GCP / Document AI (optional)
    google_application_credentials: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    gcp_project_id: str | None = os.getenv("GCP_PROJECT_ID")
    gcp_location: str = os.getenv("GCP_LOCATION", "us")
    use_google_doc_ai: bool = os.getenv("USE_GOOGLE_DOC_AI", "false").lower() == "true"
    doc_ai_processor_id: str | None = os.getenv("DOC_AI_PROCESSOR_ID")
    
    # Vertex Chat (optional) - embeddings stay OpenAI
    use_vertex_chat: bool = os.getenv("USE_VERTEX_CHAT", "false").lower() == "true"
    vertex_chat_model: str = os.getenv("VERTEX_CHAT_MODEL", "gemini-1.5-pro")

settings = Settings()

def has_commercial_license() -> bool:
    """Check if a valid commercial license is available"""
    license_key = os.getenv("VECTORPENTER_LICENSE_KEY")
    if not license_key:
        return False
    
    # TODO: Implement actual license validation
    # For now, any non-empty key is considered valid
    return len(license_key.strip()) > 0

def validate_license_key(license_key: str) -> bool:
    """Validate a commercial license key"""
    if not license_key:
        return False
    
    # TODO: Implement actual license validation logic
    # This could include:
    # - API call to license server
    # - Cryptographic signature verification
    # - Expiration date checking
    # - Feature entitlement validation
    
    # Placeholder: basic format check
    return len(license_key.strip()) >= 10

def require_commercial_license(feature_name: str = "this feature"):
    """Require commercial license for a feature"""
    if not has_commercial_license():
        from core.logging import logger
        logger.warning(f"Commercial license required for {feature_name}")
        logger.info("Get your license at: https://machinecraft.tech/vectorpenter/pricing")
        return False
    return True

def is_docai_enabled() -> bool:
    """Check if Document AI is enabled (manual override or auto-upgrade)"""
    return settings.use_google_doc_ai or (
        settings.google_application_credentials and 
        settings.gcp_project_id and 
        settings.doc_ai_processor_id
    )

def is_vertex_chat_enabled() -> bool:
    """Check if Vertex AI chat is enabled"""
    return settings.use_vertex_chat and settings.gcp_project_id and settings.google_application_credentials
