"""
Resilience and error handling utilities for Vectorpenter
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Optional, Type, Union, List
from dataclasses import dataclass
import logging

from tenacity import (
    retry, stop_after_attempt, wait_exponential, 
    retry_if_exception_type, before_sleep_log
)

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: Type[Exception] = Exception


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "open":
                if self._should_attempt_reset():
                    self.state = "half-open"
                else:
                    raise self.config.expected_exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.config.expected_exception as e:
                self._on_failure()
                raise e
                
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None
        
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


class VectorpenterError(Exception):
    """Base exception for Vectorpenter"""
    pass


class EmbeddingServiceError(VectorpenterError):
    """Embedding service unavailable or failed"""
    def __init__(self, service: str, original_error: str):
        super().__init__(f"Embedding service '{service}' failed: {original_error}")
        self.service = service
        self.original_error = original_error


class VectorDatabaseError(VectorpenterError):
    """Vector database operation failed"""
    def __init__(self, operation: str, original_error: str):
        super().__init__(f"Vector database {operation} failed: {original_error}")
        self.operation = operation
        self.original_error = original_error


class RerankerServiceError(VectorpenterError):
    """Reranking service failed"""
    def __init__(self, service: str, original_error: str):
        super().__init__(f"Reranker service '{service}' failed: {original_error}")
        self.service = service
        self.original_error = original_error


class SearchServiceError(VectorpenterError):
    """Search service (Typesense) failed"""
    def __init__(self, operation: str, original_error: str):
        super().__init__(f"Search service {operation} failed: {original_error}")
        self.operation = operation
        self.original_error = original_error


class GenerationServiceError(VectorpenterError):
    """LLM generation service failed"""
    def __init__(self, model: str, original_error: str):
        super().__init__(f"Generation service '{model}' failed: {original_error}")
        self.model = model
        self.original_error = original_error


# Retry decorators for different service types
def retry_embedding_service(max_attempts: int = 3):
    """Retry decorator for embedding service calls"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((EmbeddingServiceError, ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )


def retry_vector_database(max_attempts: int = 3):
    """Retry decorator for vector database operations"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((VectorDatabaseError, ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )


def retry_search_service(max_attempts: int = 2):
    """Retry decorator for search service calls"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((SearchServiceError, ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )


def retry_generation_service(max_attempts: int = 3):
    """Retry decorator for LLM generation calls"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=4, max=16),
        retry=retry_if_exception_type((GenerationServiceError, ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )


# Circuit breakers for external services
embedding_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=EmbeddingServiceError
))

vector_db_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=VectorDatabaseError
))

reranker_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=120,
    expected_exception=RerankerServiceError
))

search_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=45,
    expected_exception=SearchServiceError
))

generation_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=90,
    expected_exception=GenerationServiceError
))


def safe_execute(func: Callable, *args, fallback_value: Any = None, **kwargs) -> Any:
    """
    Safely execute a function with fallback value on error
    
    Args:
        func: Function to execute
        *args: Function arguments
        fallback_value: Value to return on error
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Function {func.__name__} failed: {e}. Using fallback value: {fallback_value}")
        return fallback_value


async def safe_execute_async(func: Callable, *args, fallback_value: Any = None, **kwargs) -> Any:
    """
    Safely execute an async function with fallback value on error
    """
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Async function {func.__name__} failed: {e}. Using fallback value: {fallback_value}")
        return fallback_value


def timeout_wrapper(timeout_seconds: int):
    """Decorator to add timeout to function calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # For sync functions, we can't easily add timeout without threading
                # This is a placeholder for timeout logic
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator


async def timeout_wrapper_async(timeout_seconds: int):
    """Decorator to add timeout to async function calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator


def graceful_degradation(primary_func: Callable, fallback_func: Callable, 
                        exception_types: Union[Type[Exception], tuple] = Exception):
    """
    Decorator for graceful degradation - try primary function, fallback on error
    
    Args:
        primary_func: Primary function to try
        fallback_func: Fallback function if primary fails
        exception_types: Exception types that trigger fallback
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return primary_func(*args, **kwargs)
            except exception_types as e:
                logger.warning(f"Primary function {primary_func.__name__} failed: {e}. "
                             f"Falling back to {fallback_func.__name__}")
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator


class HealthChecker:
    """Health checker for external services"""
    
    def __init__(self):
        self.service_status = {}
        
    async def check_service_health(self, service_name: str, health_check_func: Callable) -> bool:
        """Check health of a specific service"""
        try:
            result = await safe_execute_async(health_check_func)
            self.service_status[service_name] = {
                "healthy": True,
                "last_check": time.time(),
                "error": None
            }
            return True
        except Exception as e:
            self.service_status[service_name] = {
                "healthy": False,
                "last_check": time.time(),
                "error": str(e)
            }
            return False
    
    def get_service_status(self, service_name: str) -> dict:
        """Get current status of a service"""
        return self.service_status.get(service_name, {
            "healthy": False,
            "last_check": None,
            "error": "Never checked"
        })
    
    def get_all_status(self) -> dict:
        """Get status of all services"""
        return self.service_status.copy()


# Global health checker instance
health_checker = HealthChecker()


def validate_input(input_value: Any, validation_func: Callable, error_message: str = "Invalid input"):
    """
    Validate input using provided validation function
    
    Args:
        input_value: Value to validate
        validation_func: Function that returns True for valid input
        error_message: Error message for invalid input
        
    Raises:
        ValueError: If validation fails
    """
    try:
        if not validation_func(input_value):
            raise ValueError(error_message)
    except Exception as e:
        raise ValueError(f"{error_message}: {e}")


def log_performance(func: Callable) -> Callable:
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"Function {func.__name__} completed in {end_time - start_time:.3f}s")
            return result
        except Exception as e:
            end_time = time.time()
            logger.error(f"Function {func.__name__} failed after {end_time - start_time:.3f}s: {e}")
            raise
    return wrapper
