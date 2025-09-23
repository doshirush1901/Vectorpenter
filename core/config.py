from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    voyage_api_key: str | None = os.getenv("VOYAGE_API_KEY")
    pinecone_api_key: str | None = os.getenv("PINECONE_API_KEY")
    pinecone_index: str = os.getenv("PINECONE_INDEX", "vectorpenter")
    pinecone_cloud: str = os.getenv("PINECONE_CLOUD", "gcp")
    pinecone_region: str = os.getenv("PINECONE_REGION", "us-central1")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "default")
    db_url: str = os.getenv("DB_URL", "sqlite:///./data/vectorpenter.db")

settings = Settings()
