from __future__ import annotations
from pinecone import Pinecone, ServerlessSpec
from core.config import settings

_pc: Pinecone | None = None

def get_index():
    global _pc
    _pc = _pc or Pinecone(api_key=settings.pinecone_api_key)
    if settings.pinecone_index not in [i.name for i in _pc.list_indexes()]:
        _pc.create_index(
            name=settings.pinecone_index,
            dimension=1536,
            metric="dotproduct",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
        )
    return _pc.Index(settings.pinecone_index)
