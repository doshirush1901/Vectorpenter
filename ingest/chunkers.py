from __future__ import annotations
from typing import List, Dict

def simple_chunks(text: str, max_tokens: int = 700, overlap: int = 120) -> List[Dict]:
    # crude token approximation by words; good enough for v0
    words = text.split()
    step = max(1, max_tokens - overlap)
    chunks = []
    i = 0
    seq = 0
    while i < len(words):
        block = words[i:i+max_tokens]
        chunks.append({"seq": seq, "text": " ".join(block)})
        seq += 1
        i += step
    return chunks
