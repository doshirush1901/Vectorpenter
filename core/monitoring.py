"""
Production monitoring and observability for Vectorpenter
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import threading
from collections import defaultdict, deque

from core.logging import logger


@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    query_id: str
    query: str
    search_type: str  # vector, hybrid, hybrid+rerank
    k: int
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    results_count: int = 0
    embedding_time: Optional[float] = None
    search_time: Optional[float] = None
    rerank_time: Optional[float] = None
    generation_time: Optional[float] = None
    total_tokens: int = 0
    cost_usd: float = 0.0
    
    @property
    def duration_ms(self) -> float:
        """Total query duration in milliseconds"""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            "query_id": self.query_id,
            "query": self.query,
            "search_type": self.search_type,
            "k": self.k,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "results_count": self.results_count,
            "embedding_time": self.embedding_time,
            "search_time": self.search_time,
            "rerank_time": self.rerank_time,
            "generation_time": self.generation_time,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "timestamp": datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat()
        }


class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.query_history: deque = deque(maxlen=max_history)
        self.service_stats = defaultdict(lambda: {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency": 0.0,
            "last_error": None,
            "last_success": None
        })
        self._lock = threading.Lock()
    
    def start_query(self, query: str, search_type: str, k: int) -> str:
        """Start tracking a new query"""
        query_id = str(uuid.uuid4())
        metrics = QueryMetrics(
            query_id=query_id,
            query=query,
            search_type=search_type,
            k=k,
            start_time=time.time()
        )
        
        with self._lock:
            self.query_history.append(metrics)
        
        logger.debug(f"Started tracking query {query_id}")
        return query_id
    
    def end_query(self, query_id: str, success: bool = True, error: Optional[str] = None, 
                  results_count: int = 0, **kwargs):
        """End tracking for a query"""
        with self._lock:
            # Find the query metrics
            for metrics in reversed(self.query_history):
                if metrics.query_id == query_id:
                    metrics.end_time = time.time()
                    metrics.success = success
                    metrics.error = error
                    metrics.results_count = results_count
                    
                    # Update optional timing metrics
                    for key, value in kwargs.items():
                        if hasattr(metrics, key):
                            setattr(metrics, key, value)
                    
                    logger.debug(f"Completed tracking query {query_id}: {metrics.duration_ms:.1f}ms")
                    break
    
    def record_service_call(self, service: str, success: bool, latency: float, error: Optional[str] = None):
        """Record a service call"""
        with self._lock:
            stats = self.service_stats[service]
            stats["total_calls"] += 1
            stats["total_latency"] += latency
            
            if success:
                stats["successful_calls"] += 1
                stats["last_success"] = time.time()
            else:
                stats["failed_calls"] += 1
                stats["last_error"] = error
    
    def get_query_stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get query statistics for the specified time window"""
        cutoff_time = time.time() - (window_minutes * 60)
        
        with self._lock:
            recent_queries = [
                m for m in self.query_history 
                if m.start_time >= cutoff_time and m.end_time is not None
            ]
        
        if not recent_queries:
            return {
                "window_minutes": window_minutes,
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "avg_duration_ms": 0.0,
                "p95_duration_ms": 0.0,
                "search_types": {}
            }
        
        successful = [m for m in recent_queries if m.success]
        failed = [m for m in recent_queries if not m.success]
        durations = [m.duration_ms for m in recent_queries]
        
        # Calculate percentiles
        durations.sort()
        p95_index = int(len(durations) * 0.95)
        p95_duration = durations[p95_index] if durations else 0.0
        
        # Group by search type
        search_types = defaultdict(int)
        for m in recent_queries:
            search_types[m.search_type] += 1
        
        return {
            "window_minutes": window_minutes,
            "total_queries": len(recent_queries),
            "successful_queries": len(successful),
            "failed_queries": len(failed),
            "success_rate": len(successful) / len(recent_queries) if recent_queries else 0.0,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0.0,
            "p95_duration_ms": p95_duration,
            "search_types": dict(search_types),
            "avg_results_per_query": sum(m.results_count for m in recent_queries) / len(recent_queries) if recent_queries else 0.0
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service call statistics"""
        with self._lock:
            stats = {}
            for service, data in self.service_stats.items():
                total_calls = data["total_calls"]
                if total_calls > 0:
                    stats[service] = {
                        "total_calls": total_calls,
                        "success_rate": data["successful_calls"] / total_calls,
                        "avg_latency_ms": (data["total_latency"] / total_calls) * 1000,
                        "last_error": data["last_error"],
                        "last_success_ago_seconds": time.time() - data["last_success"] if data["last_success"] else None
                    }
            return stats
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        query_stats = self.get_query_stats(window_minutes=15)  # Last 15 minutes
        service_stats = self.get_service_stats()
        
        # Determine overall health
        is_healthy = True
        health_issues = []
        
        # Check query success rate
        if query_stats["total_queries"] > 0 and query_stats["success_rate"] < 0.9:
            is_healthy = False
            health_issues.append(f"Low query success rate: {query_stats['success_rate']:.1%}")
        
        # Check service health
        for service, stats in service_stats.items():
            if stats["success_rate"] < 0.95:
                is_healthy = False
                health_issues.append(f"Service {service} success rate: {stats['success_rate']:.1%}")
        
        return {
            "healthy": is_healthy,
            "issues": health_issues,
            "query_stats": query_stats,
            "service_stats": service_stats,
            "timestamp": datetime.now(tz=timezone.utc).isoformat()
        }


# Global metrics collector
metrics_collector = MetricsCollector()


def track_query(search_type: str = "vector"):
    """Decorator to track query performance"""
    def decorator(func):
        def wrapper(query: str, k: int = 12, **kwargs):
            query_id = metrics_collector.start_query(query, search_type, k)
            
            try:
                start_time = time.time()
                result = func(query, k=k, **kwargs)
                end_time = time.time()
                
                # Count results
                results_count = len(result) if isinstance(result, list) else 1
                
                metrics_collector.end_query(
                    query_id, 
                    success=True, 
                    results_count=results_count,
                    total_time=end_time - start_time
                )
                
                return result
                
            except Exception as e:
                metrics_collector.end_query(query_id, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator


def track_service_call(service_name: str):
    """Decorator to track service call performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                latency = end_time - start_time
                
                metrics_collector.record_service_call(service_name, True, latency)
                logger.debug(f"Service {service_name} call succeeded in {latency*1000:.1f}ms")
                
                return result
                
            except Exception as e:
                end_time = time.time()
                latency = end_time - start_time
                
                metrics_collector.record_service_call(service_name, False, latency, str(e))
                logger.warning(f"Service {service_name} call failed after {latency*1000:.1f}ms: {e}")
                
                raise
        
        return wrapper
    return decorator


class PerformanceProfiler:
    """Simple performance profiler for development"""
    
    def __init__(self):
        self.timers = {}
    
    def start_timer(self, name: str):
        """Start a named timer"""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End a named timer and return duration"""
        if name not in self.timers:
            logger.warning(f"Timer {name} was not started")
            return 0.0
        
        duration = time.time() - self.timers[name]
        del self.timers[name]
        
        logger.debug(f"Timer {name}: {duration*1000:.1f}ms")
        return duration
    
    def profile(self, name: str):
        """Context manager for profiling code blocks"""
        class ProfileContext:
            def __init__(self, profiler, timer_name):
                self.profiler = profiler
                self.timer_name = timer_name
            
            def __enter__(self):
                self.profiler.start_timer(self.timer_name)
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = self.profiler.end_timer(self.timer_name)
                if exc_type is not None:
                    logger.error(f"Profiled block {self.timer_name} failed after {duration*1000:.1f}ms")
        
        return ProfileContext(self, name)


# Global profiler instance
profiler = PerformanceProfiler()


def log_system_info():
    """Log system information for debugging"""
    import psutil
    import platform
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3)
        }
        
        logger.info(f"System info: {json.dumps(system_info, indent=2)}")
        
    except ImportError:
        logger.warning("psutil not available, skipping system info logging")
    except Exception as e:
        logger.warning(f"Failed to collect system info: {e}")


def create_correlation_id() -> str:
    """Create a correlation ID for request tracing"""
    return str(uuid.uuid4())[:8]


class RequestTracker:
    """Track requests across the system with correlation IDs"""
    
    def __init__(self):
        self.active_requests = {}
        self._lock = threading.Lock()
    
    def start_request(self, correlation_id: str, operation: str, **metadata):
        """Start tracking a request"""
        with self._lock:
            self.active_requests[correlation_id] = {
                "operation": operation,
                "start_time": time.time(),
                "metadata": metadata
            }
        
        logger.info(f"[{correlation_id}] Started {operation}", extra={"correlation_id": correlation_id})
    
    def end_request(self, correlation_id: str, success: bool = True, error: Optional[str] = None):
        """End tracking a request"""
        with self._lock:
            if correlation_id in self.active_requests:
                request_info = self.active_requests.pop(correlation_id)
                duration = time.time() - request_info["start_time"]
                
                log_data = {
                    "operation": request_info["operation"],
                    "duration_ms": duration * 1000,
                    "success": success,
                    "correlation_id": correlation_id
                }
                
                if error:
                    log_data["error"] = error
                    logger.error(f"[{correlation_id}] Failed {request_info['operation']}: {error}", extra=log_data)
                else:
                    logger.info(f"[{correlation_id}] Completed {request_info['operation']} in {duration*1000:.1f}ms", extra=log_data)
    
    def get_active_requests(self) -> Dict[str, Any]:
        """Get currently active requests"""
        with self._lock:
            return self.active_requests.copy()


# Global request tracker
request_tracker = RequestTracker()


def with_correlation_id(operation: str):
    """Decorator to add correlation ID tracking to functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            correlation_id = create_correlation_id()
            request_tracker.start_request(correlation_id, operation)
            
            try:
                result = func(*args, **kwargs)
                request_tracker.end_request(correlation_id, success=True)
                return result
            except Exception as e:
                request_tracker.end_request(correlation_id, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator


class AlertManager:
    """Simple alerting for critical issues"""
    
    def __init__(self):
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "avg_latency_ms": 5000,  # 5 second average latency
            "service_failure_rate": 0.05  # 5% service failure rate
        }
        self.last_alert_times = {}
        self.alert_cooldown = 300  # 5 minutes between same alerts
    
    def check_and_alert(self):
        """Check metrics and send alerts if thresholds exceeded"""
        query_stats = metrics_collector.get_query_stats(window_minutes=15)
        service_stats = metrics_collector.get_service_stats()
        
        current_time = time.time()
        
        # Check query error rate
        if (query_stats["total_queries"] > 10 and 
            query_stats["success_rate"] < (1 - self.alert_thresholds["error_rate"])):
            
            alert_key = "high_error_rate"
            if self._should_send_alert(alert_key, current_time):
                self._send_alert(
                    "High Error Rate",
                    f"Query success rate is {query_stats['success_rate']:.1%} "
                    f"(threshold: {(1-self.alert_thresholds['error_rate']):.1%})"
                )
        
        # Check average latency
        if query_stats["avg_duration_ms"] > self.alert_thresholds["avg_latency_ms"]:
            alert_key = "high_latency"
            if self._should_send_alert(alert_key, current_time):
                self._send_alert(
                    "High Latency",
                    f"Average query duration is {query_stats['avg_duration_ms']:.1f}ms "
                    f"(threshold: {self.alert_thresholds['avg_latency_ms']}ms)"
                )
        
        # Check service failure rates
        for service, stats in service_stats.items():
            if stats["success_rate"] < (1 - self.alert_thresholds["service_failure_rate"]):
                alert_key = f"service_failure_{service}"
                if self._should_send_alert(alert_key, current_time):
                    self._send_alert(
                        f"Service Failure: {service}",
                        f"Service {service} success rate is {stats['success_rate']:.1%}"
                    )
    
    def _should_send_alert(self, alert_key: str, current_time: float) -> bool:
        """Check if enough time has passed since last alert"""
        last_alert = self.last_alert_times.get(alert_key, 0)
        return current_time - last_alert >= self.alert_cooldown
    
    def _send_alert(self, title: str, message: str):
        """Send an alert (placeholder implementation)"""
        self.last_alert_times[title.lower().replace(" ", "_")] = time.time()
        
        # For now, just log the alert
        logger.critical(f"ALERT: {title} - {message}")
        
        # TODO: Implement actual alerting (email, Slack, etc.)
        # This could integrate with:
        # - Email notifications
        # - Slack webhooks
        # - PagerDuty
        # - Custom webhook endpoints


# Global alert manager
alert_manager = AlertManager()


def health_check() -> Dict[str, Any]:
    """Perform comprehensive health check"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "version": "0.1.0",
        "uptime_seconds": time.time() - start_time if 'start_time' in globals() else 0
    }
    
    try:
        # Get metrics summary
        health_summary = metrics_collector.get_health_summary()
        health_data.update(health_summary)
        
        # Check if any critical issues
        if not health_summary["healthy"]:
            health_data["status"] = "degraded"
        
        # Add active request count
        active_requests = request_tracker.get_active_requests()
        health_data["active_requests"] = len(active_requests)
        
        # System resource check
        try:
            import psutil
            health_data["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            health_data["system"] = {"status": "psutil not available"}
        
    except Exception as e:
        health_data["status"] = "error"
        health_data["error"] = str(e)
        logger.error(f"Health check failed: {e}")
    
    return health_data


# Track startup time
start_time = time.time()


def initialize_monitoring():
    """Initialize monitoring components"""
    logger.info("Initializing Vectorpenter monitoring...")
    log_system_info()
    
    # Log startup completion
    logger.info("Monitoring initialization completed")


if __name__ == "__main__":
    # Example usage
    initialize_monitoring()
    
    # Simulate some metrics
    query_id = metrics_collector.start_query("test query", "vector", 12)
    time.sleep(0.1)  # Simulate processing
    metrics_collector.end_query(query_id, success=True, results_count=5)
    
    # Print health check
    import json
    print(json.dumps(health_check(), indent=2))
