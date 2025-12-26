"""
AI CAPABILITY MANAGER - CAPABILITY-AWARE FAIL-LOUD SYSTEM

This module tracks the global status of AI capabilities across the application.

CRITICAL DISTINCTION:
- IMPLEMENTATION_INVALID: Code/architecture error - system is broken
- OPERATIONALLY_LIMITED: External resource constraint - system works but capability temporarily unavailable

PRINCIPLE: A missing external capability (quota, outage) must NEVER invalidate a correct implementation.
"""

from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel
import logging
import time

logger = logging.getLogger(__name__)


class CapabilityState(str, Enum):
    """
    State of an AI capability.
    
    AVAILABLE: Fully operational
    LIMITED: Working but degraded (e.g., slow, fallback model)
    QUOTA_EXCEEDED: External quota limit reached - NOT an implementation failure
    OFFLINE: Provider unreachable - external issue
    NOT_CONFIGURED: Missing API key or credentials - configuration issue
    UNKNOWN: Status not yet determined
    """
    AVAILABLE = "available"
    LIMITED = "limited"
    QUOTA_EXCEEDED = "quota_exceeded"
    OFFLINE = "offline"
    NOT_CONFIGURED = "not_configured"
    UNKNOWN = "unknown"


class StatusCategory(str, Enum):
    """
    Category distinguishes implementation errors from operational limits.
    
    IMPLEMENTATION_VALID: The system is correctly configured
    IMPLEMENTATION_INVALID: Code/architecture error (bug)
    OPERATIONALLY_LIMITED: External resource constraint (not a bug)
    """
    IMPLEMENTATION_VALID = "implementation_valid"
    IMPLEMENTATION_INVALID = "implementation_invalid"
    OPERATIONALLY_LIMITED = "operationally_limited"


class CapabilityStatus(BaseModel):
    """Status of a single AI capability."""
    state: CapabilityState
    category: StatusCategory = StatusCategory.IMPLEMENTATION_VALID
    message: Optional[str] = None
    user_message: Optional[str] = None  # User-facing explanation
    last_updated_ts: float = 0.0
    resume_hint: Optional[str] = None  # Hint for when capability will resume
    
    def to_api_dict(self) -> Dict[str, Any]:
        """Serialize for API response."""
        return {
            "state": self.state.value,
            "category": self.category.value,
            "message": self.message,
            "user_message": self.user_message,
            "last_updated_ts": self.last_updated_ts,
            "resume_hint": self.resume_hint,
            "is_operational_limit": self.category == StatusCategory.OPERATIONALLY_LIMITED,
            "is_implementation_error": self.category == StatusCategory.IMPLEMENTATION_INVALID,
        }


class GlobalCapabilityStatus(BaseModel):
    """Aggregated global capability status for the entire system."""
    overall_state: CapabilityState
    overall_category: StatusCategory
    capabilities: Dict[str, CapabilityStatus]
    summary_message: str
    user_visible_message: str
    timestamp: float


class AICapabilityManager:
    """
    Singleton manager for AI capability status across the application.
    
    RESPONSIBILITIES:
    1. Track status of each AI capability (text gen, image gen, etc.)
    2. Distinguish between implementation errors and operational limits
    3. Provide global status for UI display
    4. Emit clear, user-facing messages
    """
    _instance = None
    _status: Dict[str, CapabilityStatus] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AICapabilityManager, cls).__new__(cls)
            # Initialize with all known capabilities
            cls._instance._status = {
                "image_generation": CapabilityStatus(
                    state=CapabilityState.UNKNOWN,
                    category=StatusCategory.IMPLEMENTATION_VALID,
                    message="Status not yet determined",
                    user_message="Image generation status is being determined..."
                ),
                "text_generation": CapabilityStatus(
                    state=CapabilityState.UNKNOWN,
                    category=StatusCategory.IMPLEMENTATION_VALID,
                    message="Status not yet determined",
                    user_message="Text generation status is being determined..."
                ),
            }
        return cls._instance

    def report_status(
        self,
        capability: str,
        state: CapabilityState,
        message: str = None,
        category: StatusCategory = None,
        user_message: str = None,
        resume_hint: str = None
    ):
        """
        Update the status of a specific AI capability.
        
        Args:
            capability: Capability identifier (e.g., "image_generation")
            state: Current state of the capability
            message: Technical message for logs
            category: Whether this is an implementation error or operational limit
            user_message: User-facing explanation
            resume_hint: When the capability might resume
        """
        # Auto-detect category from state if not provided
        if category is None:
            if state == CapabilityState.QUOTA_EXCEEDED:
                category = StatusCategory.OPERATIONALLY_LIMITED
            elif state == CapabilityState.OFFLINE:
                category = StatusCategory.OPERATIONALLY_LIMITED
            elif state == CapabilityState.NOT_CONFIGURED:
                category = StatusCategory.IMPLEMENTATION_INVALID  # Config is an implementation responsibility
            elif state == CapabilityState.AVAILABLE:
                category = StatusCategory.IMPLEMENTATION_VALID
            else:
                category = StatusCategory.IMPLEMENTATION_VALID
        
        # Generate user-facing message if not provided
        if user_message is None:
            user_message = self._generate_user_message(capability, state, category, resume_hint)
        
        if capability not in self._status:
            logger.warning(f"Reporting status for unknown capability: {capability}")
            
        previous_state = self._status.get(capability, CapabilityStatus(state=CapabilityState.UNKNOWN)).state
        
        self._status[capability] = CapabilityStatus(
            state=state,
            category=category,
            message=message,
            user_message=user_message,
            last_updated_ts=time.time(),
            resume_hint=resume_hint
        )
        
        if previous_state != state:
            logger.info(
                f"AI Capability '{capability}' transitioned: {previous_state} -> {state}. "
                f"Category: {category.value}. Msg: {message}"
            )

    def _generate_user_message(
        self,
        capability: str,
        state: CapabilityState,
        category: StatusCategory,
        resume_hint: str = None
    ) -> str:
        """Generate a user-facing message based on state and category."""
        cap_name = capability.replace("_", " ").title()
        
        if state == CapabilityState.AVAILABLE:
            return f"{cap_name} is fully operational."
        
        elif state == CapabilityState.QUOTA_EXCEEDED:
            base = f"{cap_name} is temporarily unavailable due to quota limits."
            if category == StatusCategory.OPERATIONALLY_LIMITED:
                base += " The system is correctly configured and will resume automatically."
            if resume_hint:
                base += f" {resume_hint}"
            return base
        
        elif state == CapabilityState.OFFLINE:
            base = f"{cap_name} is temporarily offline due to provider issues."
            if category == StatusCategory.OPERATIONALLY_LIMITED:
                base += " This is not a system configuration issue."
            return base
        
        elif state == CapabilityState.NOT_CONFIGURED:
            return f"{cap_name} is not configured. Please set the required API key."
        
        elif state == CapabilityState.LIMITED:
            return f"{cap_name} is operating in degraded mode."
        
        else:
            return f"{cap_name} status is being determined..."

    def get_status(self, capability: str) -> CapabilityStatus:
        """Get status of a specific capability."""
        return self._status.get(capability, CapabilityStatus(state=CapabilityState.UNKNOWN))

    def get_all_statuses(self) -> Dict[str, CapabilityStatus]:
        """Get all capability statuses."""
        return self._status
    
    def get_global_status(self) -> GlobalCapabilityStatus:
        """
        Get aggregated global status for UI display.
        
        This determines the overall system health and provides
        a single message for the status bar.
        """
        # Determine overall state (worst of all capabilities)
        state_priority = [
            CapabilityState.UNKNOWN,
            CapabilityState.AVAILABLE,
            CapabilityState.LIMITED,
            CapabilityState.OFFLINE,
            CapabilityState.NOT_CONFIGURED,
            CapabilityState.QUOTA_EXCEEDED,
        ]
        
        worst_state = CapabilityState.AVAILABLE
        worst_category = StatusCategory.IMPLEMENTATION_VALID
        limited_capabilities = []
        
        for cap_name, status in self._status.items():
            if state_priority.index(status.state) > state_priority.index(worst_state):
                worst_state = status.state
            
            if status.category == StatusCategory.IMPLEMENTATION_INVALID:
                worst_category = StatusCategory.IMPLEMENTATION_INVALID
            elif status.category == StatusCategory.OPERATIONALLY_LIMITED and worst_category != StatusCategory.IMPLEMENTATION_INVALID:
                worst_category = StatusCategory.OPERATIONALLY_LIMITED
            
            if status.state not in [CapabilityState.AVAILABLE, CapabilityState.UNKNOWN]:
                limited_capabilities.append((cap_name, status))
        
        # Generate summary message
        if worst_state == CapabilityState.AVAILABLE:
            summary = "All AI capabilities fully operational"
            user_message = "✓ System fully operational"
        elif worst_category == StatusCategory.OPERATIONALLY_LIMITED:
            cap_names = [cap.replace("_", " ").title() for cap, _ in limited_capabilities]
            summary = f"Operational limits on: {', '.join(cap_names)}"
            user_message = f"⚠️ Some features temporarily limited (external constraint) — System is correctly configured"
        elif worst_category == StatusCategory.IMPLEMENTATION_INVALID:
            summary = "Configuration issue detected"
            user_message = "⚙️ Configuration required — Please check settings"
        else:
            summary = "Status being determined"
            user_message = "🔄 Checking system status..."
        
        return GlobalCapabilityStatus(
            overall_state=worst_state,
            overall_category=worst_category,
            capabilities=self._status,
            summary_message=summary,
            user_visible_message=user_message,
            timestamp=time.time()
        )
    
    def to_api_response(self) -> Dict[str, Any]:
        """
        Convert to API-friendly format for frontend consumption.
        
        This is the primary method for exposing capability status to the UI.
        """
        global_status = self.get_global_status()
        
        return {
            "overall": {
                "state": global_status.overall_state.value,
                "category": global_status.overall_category.value,
                "summary": global_status.summary_message,
                "user_message": global_status.user_visible_message,
                "is_operational_limit": global_status.overall_category == StatusCategory.OPERATIONALLY_LIMITED,
                "is_implementation_valid": global_status.overall_category != StatusCategory.IMPLEMENTATION_INVALID,
            },
            "capabilities": {
                name: status.to_api_dict()
                for name, status in self._status.items()
            },
            "timestamp": global_status.timestamp
        }


# Global singleton accessor
def get_capability_manager() -> AICapabilityManager:
    """Get the global AI capability manager instance."""
    return AICapabilityManager()
