"""
Google Cloud Translation integration for Vectorpenter
Auto-translate non-English documents to English before DLP + embedding
"""

from __future__ import annotations
from typing import Tuple, Optional
from core.config import settings
from core.logging import logger

# Global client for reuse
_client = None

def _client_init():
    """Initialize Translation client (lazy loading)"""
    global _client
    if _client is None:
        try:
            from google.cloud import translate_v3 as translate
            _client = translate.TranslationServiceClient()
            logger.debug("Translation client initialized")
        except ImportError:
            raise ImportError("Google Cloud Translation libraries not installed")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Translation client: {e}")
    return _client


def translate_text(text: str, target_lang: str = "en") -> Tuple[str, dict]:
    """
    Translate text to target language using Cloud Translation
    
    Args:
        text: Text to translate
        target_lang: Target language code (default: "en")
        
    Returns:
        Tuple of (translated_text, metadata)
    """
    if not text.strip():
        return text, {"translated": False, "reason": "empty_text"}
    
    # Check if translation is enabled and configured
    if not settings.gcp_project_id:
        logger.warning("GCP_PROJECT_ID not configured for translation")
        return text, {"translated": False, "reason": "no_project_id"}
    
    try:
        client = _client_init()
        
        # Prepare translation request
        parent = f"projects/{settings.gcp_project_id}/locations/{settings.gcp_location}"
        
        logger.debug(f"Translating text to {target_lang}: {len(text)} characters")
        
        # Call Translation API
        response = client.translate_text(
            parent=parent,
            contents=[text],
            target_language_code=target_lang,
            mime_type="text/plain"
        )
        
        if response.translations and len(response.translations) > 0:
            translation = response.translations[0]
            translated_text = translation.translated_text
            detected_lang = translation.detected_language_code
            
            # Check if translation actually occurred
            if detected_lang == target_lang:
                logger.info(f"Text already in target language ({target_lang}), no translation needed")
                return text, {
                    "translated": False, 
                    "reason": "already_target_language",
                    "detected_language": detected_lang
                }
            
            logger.info(f"Translation completed: {detected_lang} -> {target_lang} ({len(translated_text)} chars)")
            
            return translated_text, {
                "translated": True,
                "source_language": detected_lang,
                "target_language": target_lang,
                "original_length": len(text),
                "translated_length": len(translated_text)
            }
        else:
            logger.warning("Translation API returned empty response")
            return text, {"translated": False, "reason": "empty_response"}
        
    except ImportError as e:
        logger.warning(f"Google Cloud Translation libraries not available: {e}")
        return text, {"translated": False, "reason": "libraries_not_installed"}
    
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text, {"translated": False, "reason": "translation_error", "error": str(e)}


def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of text
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code or None if detection fails
    """
    if not text.strip():
        return None
    
    try:
        client = _client_init()
        parent = f"projects/{settings.gcp_project_id}/locations/{settings.gcp_location}"
        
        # Use a sample of text for language detection (first 1000 chars)
        sample_text = text[:1000]
        
        response = client.detect_language(
            parent=parent,
            content=sample_text,
            mime_type="text/plain"
        )
        
        if response.languages and len(response.languages) > 0:
            detected_lang = response.languages[0].language_code
            confidence = response.languages[0].confidence
            
            logger.debug(f"Language detected: {detected_lang} (confidence: {confidence:.2f})")
            return detected_lang
        
        return None
        
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return None


def should_translate(text: str, target_lang: str = "en") -> bool:
    """
    Determine if text should be translated based on configuration and content
    
    Args:
        text: Text to check
        target_lang: Target language
        
    Returns:
        True if text should be translated, False otherwise
    """
    if not text.strip():
        return False
    
    # Check if translation is enabled
    if not settings.use_translation:
        return False
    
    # Check minimum character threshold
    if len(text.strip()) < settings.translate_min_chars:
        logger.debug(f"Text too short for translation: {len(text)} < {settings.translate_min_chars} chars")
        return False
    
    # Detect language and decide
    detected_lang = detect_language(text)
    
    if detected_lang is None:
        logger.debug("Could not detect language, skipping translation")
        return False
    
    if detected_lang == target_lang:
        logger.debug(f"Text already in target language ({target_lang}), no translation needed")
        return False
    
    logger.info(f"Text should be translated: {detected_lang} -> {target_lang}")
    return True


def is_translation_available() -> bool:
    """
    Check if Cloud Translation is available and properly configured
    
    Returns:
        True if translation can be used, False otherwise
    """
    try:
        # Check if libraries are installed
        from google.cloud import translate_v3 as translate
        
        # Check configuration
        if not all([
            settings.gcp_project_id,
            settings.google_application_credentials
        ]):
            return False
        
        # Check if credentials file exists
        if settings.google_application_credentials:
            from pathlib import Path
            creds_path = Path(settings.google_application_credentials)
            if not creds_path.exists():
                logger.warning(f"Google credentials file not found: {creds_path}")
                return False
        
        return True
        
    except ImportError:
        logger.debug("Google Cloud Translation libraries not installed")
        return False
    except Exception as e:
        logger.warning(f"Translation availability check failed: {e}")
        return False


def test_translation_connection() -> bool:
    """
    Test Cloud Translation connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        if not is_translation_available():
            logger.warning("Translation not properly configured")
            return False
        
        # Test with a simple translation
        test_text = "Hello, world!"
        translated_text, metadata = translate_text(test_text, target_lang="es")
        
        if metadata.get("translated", False):
            logger.info("Translation connection successful")
            return True
        else:
            logger.info("Translation connection successful (no translation needed)")
            return True
        
    except Exception as e:
        logger.warning(f"Translation connection test failed: {e}")
        return False


def estimate_translation_cost(char_count: int) -> dict:
    """
    Estimate Cloud Translation cost
    
    Args:
        char_count: Number of characters to translate
        
    Returns:
        Dictionary with cost estimates
    """
    # Cloud Translation pricing (as of 2025)
    # $20 per 1M characters
    cost_per_million_chars = 20.0
    
    cost = (char_count / 1_000_000) * cost_per_million_chars
    
    return {
        "characters": char_count,
        "estimated_cost_usd": round(cost, 6),
        "cost_per_million": cost_per_million_chars,
        "note": "Estimate based on $20 per 1M characters"
    }


def get_supported_languages() -> List[str]:
    """
    Get list of supported language codes
    
    Returns:
        List of supported language codes
    """
    try:
        client = _client_init()
        parent = f"projects/{settings.gcp_project_id}/locations/{settings.gcp_location}"
        
        response = client.get_supported_languages(parent=parent)
        
        language_codes = [lang.language_code for lang in response.languages]
        logger.debug(f"Retrieved {len(language_codes)} supported languages")
        
        return language_codes
        
    except Exception as e:
        logger.warning(f"Failed to get supported languages: {e}")
        # Return common language codes as fallback
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "bn", "ur", "fa", "tr", "pl", "nl", "sv", "da"
        ]
