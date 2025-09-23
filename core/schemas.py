from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class IngestResult(BaseModel):
    documents: int
    chunks: int

class QueryResult(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
