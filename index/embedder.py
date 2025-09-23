from __future__ import annotations
from typing import List
from core.config import settings
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"

_client: OpenAI | None = None

def client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def embed_texts(texts: List[str]) -> List[List[float]]:
    c = client()
    resp = c.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]
