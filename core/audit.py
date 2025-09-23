"""
Audit logging for Vectorpenter security and compliance
"""

from __future__ import annotations
import time
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from core.logging import logger

class AuditEventType(str, Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    QUERY_EXECUTED = "query_executed"
    DOCUMENT_INGESTED = "document_ingested"
    INDEX_BUILT = "index_built"
    CONFIG_CHANGED = "config_changed"
    ERROR_OCCURRED = "error_occurred"
    SECURITY_VIOLATION = "security_violation"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"

@dataclass
class AuditEvent:
    """Audit event model"""
    event_type: AuditEventType
    timestamp: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return asdict(self)

class AuditLogger:
    """Centralized audit logging"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path("logs/audit.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def log_event(self, event: AuditEvent):
        """Log an audit event"""
        try:
            # Log to structured logger
            logger.info(
                f"AUDIT: {event.event_type}",
                extra={
                    "audit_event": event.to_dict(),
                    "event_type": event.event_type,
                    "user_id": event.user_id,
                    "success": event.success
                }
            )
            
            # Also log to dedicated audit file
            with open(self.log_file, "a", encoding="utf-8") as f:
                audit_line = json.dumps(event.to_dict()) + "\n"
                f.write(audit_line)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def log_query(self, user_id: str, query: str, results_count: int, 
                  search_type: str, success: bool = True, error: Optional[str] = None):
        """Log a query execution"""
        event = AuditEvent(
            event_type=AuditEventType.QUERY_EXECUTED,
            timestamp=time.time(),
            user_id=user_id,
            resource="query",
            action="execute",
            details={
                "query_length": len(query),
                "results_count": results_count,
                "search_type": search_type
            },
            success=success,
            error_message=error
        )
        self.log_event(event)
    
    def log_ingestion(self, user_id: str, file_path: str, documents_count: int, 
                     chunks_count: int, success: bool = True, error: Optional[str] = None):
        """Log document ingestion"""
        event = AuditEvent(
            event_type=AuditEventType.DOCUMENT_INGESTED,
            timestamp=time.time(),
            user_id=user_id,
            resource="document",
            action="ingest",
            details={
                "file_path": file_path,
                "documents_count": documents_count,
                "chunks_count": chunks_count
            },
            success=success,
            error_message=error
        )
        self.log_event(event)
    
    def log_security_violation(self, user_id: Optional[str], violation_type: str, 
                              details: Dict[str, Any], ip_address: Optional[str] = None):
        """Log security violation"""
        event = AuditEvent(
            event_type=AuditEventType.SECURITY_VIOLATION,
            timestamp=time.time(),
            user_id=user_id,
            ip_address=ip_address,
            resource="security",
            action="violation",
            details={
                "violation_type": violation_type,
                **details
            },
            success=False
        )
        self.log_event(event)
    
    def log_user_action(self, event_type: AuditEventType, user_id: str, 
                       details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None):
        """Log user authentication actions"""
        event = AuditEvent(
            event_type=event_type,
            timestamp=time.time(),
            user_id=user_id,
            ip_address=ip_address,
            resource="user",
            action=event_type.value,
            details=details or {},
            success=True
        )
        self.log_event(event)

# Global audit logger
audit_logger = AuditLogger()

def audit_query(user_id: str, query: str, results_count: int, search_type: str):
    """Decorator for auditing query executions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                audit_logger.log_query(user_id, query, results_count, search_type, success=True)
                return result
            except Exception as e:
                audit_logger.log_query(user_id, query, 0, search_type, success=False, error=str(e))
                raise
        return wrapper
    return decorator

def audit_ingestion(user_id: str, file_path: str):
    """Decorator for auditing document ingestion"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                docs_count = result.get("documents", 0)
                chunks_count = result.get("chunks", 0)
                audit_logger.log_ingestion(user_id, file_path, docs_count, chunks_count, success=True)
                return result
            except Exception as e:
                audit_logger.log_ingestion(user_id, file_path, 0, 0, success=False, error=str(e))
                raise
        return wrapper
    return decorator
