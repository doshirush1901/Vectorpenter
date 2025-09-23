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
    cohere_api_key: str | None = os.getenv("COHERE_API_KEY")
    
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

settings = Settings()
