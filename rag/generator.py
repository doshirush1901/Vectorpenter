from __future__ import annotations
from core.config import settings
from openai import OpenAI

SYSTEM = (
    "You are Vectorpenter: answer ONLY using the provided Context Pack. "
    "If the context is insufficient, say what's missing and suggest a next step. "
    "Cite with bracketed numbers like [#1], [#2] that refer to the Context Pack entries."
)

_llm: OpenAI | None = None

def llm() -> OpenAI:
    global _llm
    _llm = _llm or OpenAI(api_key=settings.openai_api_key)
    return _llm


def answer(question: str, context_pack: str) -> str:
    resp = llm().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"QUESTION: {question}\n\nCONTEXT PACK:\n{context_pack}"},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
