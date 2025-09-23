from __future__ import annotations
from core.config import settings, is_vertex_chat_enabled
from core.logging import logger
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
    """
    Generate answer using configured chat provider (Vertex or OpenAI)
    Embeddings always use OpenAI regardless of chat provider
    """
    user_prompt = f"QUESTION: {question}\n\nCONTEXT PACK:\n{context_pack}"
    
    # Check if Vertex chat is enabled
    if is_vertex_chat_enabled():
        try:
            logger.info(f"Chat provider: Vertex ({settings.vertex_chat_model})")
            from gcp.vertex import vertex_chat
            
            response = vertex_chat(
                system=SYSTEM,
                user=user_prompt,
                model_name=settings.vertex_chat_model
            )
            
            return response
            
        except ImportError:
            logger.warning("Google Cloud libraries not installed, falling back to OpenAI")
        except Exception as e:
            logger.warning(f"Vertex AI chat failed, falling back to OpenAI: {e}")
    
    # Default to OpenAI (or fallback from Vertex)
    logger.info("Chat provider: OpenAI (gpt-4o-mini)")
    
    try:
        resp = llm().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
        
    except Exception as e:
        logger.error(f"OpenAI chat generation failed: {e}")
        return f"I apologize, but I encountered an error while generating the response: {e}"
