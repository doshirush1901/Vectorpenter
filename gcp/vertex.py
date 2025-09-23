"""
Google Cloud Vertex AI chat integration for Vectorpenter
Optional chat provider - embeddings stay with OpenAI
"""

from __future__ import annotations
from typing import Optional
from core.config import settings
from core.logging import logger

# Global initialization flag to avoid repeated setup
_vertex_initialized = False

def _ensure_vertex_initialized():
    """Lazy initialization of Vertex AI"""
    global _vertex_initialized
    
    if _vertex_initialized:
        return
    
    try:
        from google.cloud import aiplatform
        
        if not settings.gcp_project_id:
            raise ValueError("GCP_PROJECT_ID not configured")
        
        # Initialize Vertex AI
        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.gcp_location
        )
        
        logger.info(f"Vertex AI initialized: project={settings.gcp_project_id}, location={settings.gcp_location}")
        _vertex_initialized = True
        
    except ImportError:
        raise ImportError("Google Cloud AI Platform libraries not installed")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Vertex AI: {e}")


def vertex_chat(system: str, user: str, model_name: Optional[str] = None) -> str:
    """
    Generate chat response using Vertex AI Gemini
    
    Args:
        system: System prompt/instructions
        user: User message/question
        model_name: Model to use (defaults to configured model)
        
    Returns:
        Generated response text
        
    Raises:
        ImportError: If Google Cloud libraries not installed
        RuntimeError: If Vertex AI not properly configured
        Exception: If generation fails
    """
    try:
        from google.cloud import aiplatform
        from vertexai.generative_models import GenerativeModel, Part
        
        # Ensure Vertex AI is initialized
        _ensure_vertex_initialized()
        
        # Use configured model or provided model
        model = model_name or settings.vertex_chat_model
        
        logger.debug(f"Using Vertex AI model: {model}")
        
        # Initialize the generative model
        generative_model = GenerativeModel(model)
        
        # Combine system and user messages
        # Gemini doesn't have separate system/user roles like OpenAI
        combined_prompt = f"{system}\n\nUser: {user}\n\nAssistant:"
        
        logger.debug(f"Generating response with Vertex AI: prompt_length={len(combined_prompt)}")
        
        # Generate response
        response = generative_model.generate_content(
            combined_prompt,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # Extract text from response
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                generated_text = candidate.content.parts[0].text
                
                logger.info(f"Vertex AI response generated: {len(generated_text)} characters")
                return generated_text
        
        # Fallback if no content generated
        logger.warning("Vertex AI generated empty response")
        return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        
    except ImportError as e:
        error_msg = f"Google Cloud libraries not installed: {e}"
        logger.error(error_msg)
        raise ImportError(error_msg)
    
    except Exception as e:
        error_msg = f"Vertex AI generation failed: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)


def is_vertex_available() -> bool:
    """
    Check if Vertex AI is available and properly configured
    
    Returns:
        True if Vertex AI can be used, False otherwise
    """
    try:
        # Check if libraries are installed
        from google.cloud import aiplatform
        
        # Check configuration
        if not all([
            settings.gcp_project_id,
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
        logger.debug("Google Cloud libraries not installed, Vertex AI unavailable")
        return False
    except Exception as e:
        logger.warning(f"Vertex AI availability check failed: {e}")
        return False


def test_vertex_connection() -> bool:
    """
    Test Vertex AI connection and configuration
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        if not is_vertex_available():
            logger.warning("Vertex AI not properly configured")
            return False
        
        # Initialize and test with a simple generation
        _ensure_vertex_initialized()
        
        # Test with a simple prompt
        test_response = vertex_chat(
            system="You are a helpful assistant.",
            user="Say 'Hello' if you can hear me.",
            model_name=settings.vertex_chat_model
        )
        
        if test_response and len(test_response.strip()) > 0:
            logger.info(f"Vertex AI connection successful: {settings.vertex_chat_model}")
            return True
        else:
            logger.warning("Vertex AI test generated empty response")
            return False
        
    except ImportError:
        logger.warning("Google Cloud libraries not installed")
        return False
    except Exception as e:
        logger.warning(f"Vertex AI connection test failed: {e}")
        return False


def get_vertex_models() -> list:
    """
    Get list of available Vertex AI models
    
    Returns:
        List of available model names
    """
    try:
        _ensure_vertex_initialized()
        
        # Common Gemini models available in Vertex AI
        available_models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
            "text-bison",
            "chat-bison"
        ]
        
        logger.debug(f"Available Vertex AI models: {available_models}")
        return available_models
        
    except Exception as e:
        logger.warning(f"Failed to get Vertex AI models: {e}")
        return ["gemini-1.5-pro"]  # Default fallback


def estimate_vertex_cost(input_chars: int, output_chars: int, model: str = "gemini-1.5-pro") -> dict:
    """
    Estimate Vertex AI usage cost
    
    Args:
        input_chars: Number of input characters
        output_chars: Number of output characters  
        model: Model name
        
    Returns:
        Dictionary with cost estimates
    """
    # Rough cost estimates (as of 2025) - these are approximate
    # Gemini Pro pricing is typically per 1K characters
    cost_per_1k_input = 0.00025  # $0.00025 per 1K input characters
    cost_per_1k_output = 0.0005  # $0.0005 per 1K output characters
    
    input_cost = (input_chars / 1000) * cost_per_1k_input
    output_cost = (output_chars / 1000) * cost_per_1k_output
    total_cost = input_cost + output_cost
    
    return {
        "model": model,
        "input_characters": input_chars,
        "output_characters": output_chars,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "note": "Estimates based on approximate Vertex AI pricing"
    }
