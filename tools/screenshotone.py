"""
ScreenshotOne integration for Vectorpenter
Capture webpages as images/PDFs directly into data/inputs/
"""

from __future__ import annotations
import os
import time
from pathlib import Path
from urllib.parse import urlencode
import requests
from core.logging import logger

# Output directory for screenshots
OUT_DIR = Path("data/inputs")

def fetch_url(url: str) -> Path:
    """
    Fetch a screenshot of a URL using ScreenshotOne API
    
    Args:
        url: URL to capture
        
    Returns:
        Path to saved screenshot file
        
    Raises:
        RuntimeError: If API key not configured
        requests.RequestException: If API call fails
    """
    # Ensure output directory exists
    if not OUT_DIR.exists():
        OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get configuration from environment
    base_url = os.getenv("SCREENSHOTONE_BASE", "https://api.screenshotone.com/take")
    api_key = os.getenv("SCREENSHOTONE_API_KEY", "")
    format_type = os.getenv("SCREENSHOTONE_FORMAT", "png")
    device = os.getenv("SCREENSHOTONE_DEVICE", "desktop")
    full_page = os.getenv("SCREENSHOTONE_FULL_PAGE", "true")
    block_ads = os.getenv("SCREENSHOTONE_BLOCK_ADS", "true")
    
    if not api_key:
        raise RuntimeError("SCREENSHOTONE_API_KEY missing. Set it in .env and enable USE_SCREENSHOTONE.")
    
    # Prepare API parameters
    params = {
        "access_key": api_key,
        "url": url,
        "format": format_type,
        "device_scale_factor": 1,
        "device": device,
        "full_page": str(full_page).lower(),
        "block_ads": str(block_ads).lower(),
        "cache": "false",
        "omit_background": "false",
    }
    
    # Build request URL
    query_string = urlencode(params)
    request_url = f"{base_url}?{query_string}"
    
    logger.info(f"Capturing screenshot: {url} ({format_type}, {device})")
    logger.debug(f"ScreenshotOne request: {request_url}")
    
    try:
        # Make API request
        response = requests.get(request_url, timeout=60)
        response.raise_for_status()
        
        # Generate output filename
        timestamp = int(time.time() * 1000)
        extension = "png" if format_type not in ("jpeg", "pdf") else format_type
        output_path = OUT_DIR / f"snap_{timestamp}.{extension}"
        
        # Save screenshot
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Screenshot saved: {output_path} ({len(response.content)} bytes)")
        return output_path
        
    except requests.exceptions.Timeout:
        error_msg = f"ScreenshotOne request timed out for {url}"
        logger.error(error_msg)
        raise requests.RequestException(error_msg)
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"ScreenshotOne API error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        raise requests.RequestException(error_msg)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"ScreenshotOne request failed: {e}"
        logger.error(error_msg)
        raise
    
    except Exception as e:
        error_msg = f"Unexpected error capturing screenshot: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def is_screenshotone_available() -> bool:
    """
    Check if ScreenshotOne is properly configured
    
    Returns:
        True if ScreenshotOne can be used, False otherwise
    """
    use_screenshotone = os.getenv("USE_SCREENSHOTONE", "false").lower() == "true"
    api_key = os.getenv("SCREENSHOTONE_API_KEY", "")
    
    return use_screenshotone and bool(api_key.strip())


def test_screenshotone_connection() -> bool:
    """
    Test ScreenshotOne API connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        if not is_screenshotone_available():
            logger.warning("ScreenshotOne not properly configured")
            return False
        
        # Test with a simple URL (use a reliable test page)
        test_url = "https://httpbin.org/html"
        
        # Make a test request (don't save the result)
        base_url = os.getenv("SCREENSHOTONE_BASE", "https://api.screenshotone.com/take")
        api_key = os.getenv("SCREENSHOTONE_API_KEY", "")
        
        params = {
            "access_key": api_key,
            "url": test_url,
            "format": "png",
            "device": "desktop",
            "full_page": "false",  # Faster test
            "block_ads": "true",
            "cache": "false"
        }
        
        query_string = urlencode(params)
        test_request_url = f"{base_url}?{query_string}"
        
        response = requests.head(test_request_url, timeout=10)  # HEAD request for faster test
        
        if response.status_code == 200:
            logger.info("ScreenshotOne connection successful")
            return True
        else:
            logger.warning(f"ScreenshotOne test failed: HTTP {response.status_code}")
            return False
        
    except Exception as e:
        logger.warning(f"ScreenshotOne connection test failed: {e}")
        return False


def estimate_screenshotone_cost(num_screenshots: int) -> dict:
    """
    Estimate ScreenshotOne API cost
    
    Args:
        num_screenshots: Number of screenshots to capture
        
    Returns:
        Dictionary with cost estimates
    """
    # ScreenshotOne pricing (as of 2025)
    # Typically $0.001-$0.01 per screenshot depending on plan
    cost_per_screenshot = 0.005  # Average estimate
    
    total_cost = num_screenshots * cost_per_screenshot
    
    return {
        "screenshots": num_screenshots,
        "cost_per_screenshot": cost_per_screenshot,
        "estimated_cost_usd": round(total_cost, 4),
        "note": "Estimates based on typical ScreenshotOne pricing (~$0.005/screenshot)"
    }


def get_screenshot_formats() -> List[str]:
    """
    Get list of supported screenshot formats
    
    Returns:
        List of format strings
    """
    return ["png", "jpeg", "pdf"]


def get_device_types() -> List[str]:
    """
    Get list of supported device types
    
    Returns:
        List of device type strings
    """
    return ["desktop", "tablet", "mobile"]
