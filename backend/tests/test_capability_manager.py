# TEST_REGIME: STRUCTURAL
# REQUIRES: None (capability singleton tests)
"""
TEST: AI CAPABILITY MANAGER - CAPABILITY-AWARE FAIL-LOUD BEHAVIOR

This test suite validates the critical distinction between:
- IMPLEMENTATION_INVALID: Code/architecture error (bug)
- OPERATIONALLY_LIMITED: External resource constraint (quota, outage)

NON-NEGOTIABLE: A missing external capability must NEVER invalidate a correct implementation.
"""

import pytest
import time
from backend.ai.capability_manager import (
    AICapabilityManager,
    get_capability_manager,
    CapabilityState,
    CapabilityStatus,
    StatusCategory,
    GlobalCapabilityStatus,
)


class TestCapabilityManagerSetup:
    """Test capability manager initialization and singleton behavior."""

    def test_singleton_pattern(self):
        """Manager should be a singleton."""
        manager1 = get_capability_manager()
        manager2 = get_capability_manager()
        assert manager1 is manager2

    def test_initial_capabilities_exist(self):
        """Manager should initialize with known capabilities."""
        manager = get_capability_manager()
        statuses = manager.get_all_statuses()
        
        assert "image_generation" in statuses
        assert "text_generation" in statuses

    def test_initial_state_is_unknown(self):
        """Initial state should be UNKNOWN, not FAILED."""
        # Create fresh manager by resetting singleton
        AICapabilityManager._instance = None
        manager = get_capability_manager()
        
        status = manager.get_status("image_generation")
        assert status.state == CapabilityState.UNKNOWN
        # Unknown is NOT an implementation error
        assert status.category != StatusCategory.IMPLEMENTATION_INVALID


class TestCapabilityStateTransitions:
    """Test capability state reporting and transitions."""

    def test_report_quota_exceeded(self):
        """Quota exceeded should be marked as OPERATIONALLY_LIMITED."""
        manager = get_capability_manager()
        
        manager.report_status(
            "image_generation",
            CapabilityState.QUOTA_EXCEEDED,
            message="Google Gemini quota exceeded"
        )
        
        status = manager.get_status("image_generation")
        assert status.state == CapabilityState.QUOTA_EXCEEDED
        assert status.category == StatusCategory.OPERATIONALLY_LIMITED
        assert "quota" in status.user_message.lower()
        assert "correctly configured" in status.user_message.lower()

    def test_report_offline(self):
        """Provider offline should be OPERATIONALLY_LIMITED."""
        manager = get_capability_manager()
        
        manager.report_status(
            "image_generation",
            CapabilityState.OFFLINE,
            message="Provider unreachable"
        )
        
        status = manager.get_status("image_generation")
        assert status.state == CapabilityState.OFFLINE
        assert status.category == StatusCategory.OPERATIONALLY_LIMITED

    def test_report_not_configured(self):
        """Missing configuration should be IMPLEMENTATION_INVALID."""
        manager = get_capability_manager()
        
        manager.report_status(
            "image_generation",
            CapabilityState.NOT_CONFIGURED,
            message="GEMINI_API_KEY not set"
        )
        
        status = manager.get_status("image_generation")
        assert status.state == CapabilityState.NOT_CONFIGURED
        assert status.category == StatusCategory.IMPLEMENTATION_INVALID

    def test_report_available(self):
        """Available should be IMPLEMENTATION_VALID."""
        manager = get_capability_manager()
        
        manager.report_status(
            "image_generation",
            CapabilityState.AVAILABLE,
            message="System fully operational"
        )
        
        status = manager.get_status("image_generation")
        assert status.state == CapabilityState.AVAILABLE
        assert status.category == StatusCategory.IMPLEMENTATION_VALID

    def test_custom_category_override(self):
        """Explicit category should override auto-detection."""
        manager = get_capability_manager()
        
        manager.report_status(
            "image_generation",
            CapabilityState.OFFLINE,
            category=StatusCategory.IMPLEMENTATION_INVALID,
            message="This is a code bug"
        )
        
        status = manager.get_status("image_generation")
        assert status.category == StatusCategory.IMPLEMENTATION_INVALID


class TestGlobalStatusAggregation:
    """Test global status aggregation for UI display."""

    def test_all_available_is_valid(self):
        """When all capabilities are available, global status should be valid."""
        manager = get_capability_manager()
        
        manager.report_status("image_generation", CapabilityState.AVAILABLE)
        manager.report_status("text_generation", CapabilityState.AVAILABLE)
        
        global_status = manager.get_global_status()
        assert global_status.overall_state == CapabilityState.AVAILABLE
        assert global_status.overall_category == StatusCategory.IMPLEMENTATION_VALID
        assert "operational" in global_status.user_visible_message.lower()

    def test_quota_limit_is_operational_constraint(self):
        """Quota limit should show as operational constraint, NOT implementation error."""
        manager = get_capability_manager()
        
        manager.report_status("image_generation", CapabilityState.QUOTA_EXCEEDED)
        manager.report_status("text_generation", CapabilityState.AVAILABLE)
        
        global_status = manager.get_global_status()
        assert global_status.overall_category == StatusCategory.OPERATIONALLY_LIMITED
        assert "correctly configured" in global_status.user_visible_message.lower()

    def test_config_issue_is_implementation_error(self):
        """Configuration issue should show as implementation error."""
        manager = get_capability_manager()
        
        manager.report_status("image_generation", CapabilityState.NOT_CONFIGURED)
        manager.report_status("text_generation", CapabilityState.AVAILABLE)
        
        global_status = manager.get_global_status()
        assert global_status.overall_category == StatusCategory.IMPLEMENTATION_INVALID


class TestAPIResponse:
    """Test API response format for frontend consumption."""

    def test_api_response_structure(self):
        """API response should have correct structure."""
        manager = get_capability_manager()
        manager.report_status("image_generation", CapabilityState.QUOTA_EXCEEDED)
        
        response = manager.to_api_response()
        
        # Top-level structure
        assert "overall" in response
        assert "capabilities" in response
        assert "timestamp" in response
        
        # Overall structure
        assert "state" in response["overall"]
        assert "category" in response["overall"]
        assert "is_operational_limit" in response["overall"]
        assert "is_implementation_valid" in response["overall"]
        
        # Capability structure
        assert "image_generation" in response["capabilities"]
        cap = response["capabilities"]["image_generation"]
        assert "is_operational_limit" in cap
        assert "is_implementation_error" in cap

    def test_api_response_flags_for_quota_limit(self):
        """API response should have correct flags for quota limit."""
        manager = get_capability_manager()
        manager.report_status("image_generation", CapabilityState.QUOTA_EXCEEDED)
        
        response = manager.to_api_response()
        
        # Overall flags
        assert response["overall"]["is_operational_limit"] is True
        assert response["overall"]["is_implementation_valid"] is True
        
        # Capability flags
        cap = response["capabilities"]["image_generation"]
        assert cap["is_operational_limit"] is True
        assert cap["is_implementation_error"] is False

    def test_api_response_flags_for_config_issue(self):
        """API response should have correct flags for config issue."""
        manager = get_capability_manager()
        manager.report_status("image_generation", CapabilityState.NOT_CONFIGURED)
        
        response = manager.to_api_response()
        
        # Capability flags
        cap = response["capabilities"]["image_generation"]
        assert cap["is_operational_limit"] is False
        assert cap["is_implementation_error"] is True


class TestUserMessages:
    """Test user-facing message generation."""

    def test_quota_message_is_reassuring(self):
        """Quota exceeded message should reassure user that system works."""
        manager = get_capability_manager()
        manager.report_status("image_generation", CapabilityState.QUOTA_EXCEEDED)
        
        status = manager.get_status("image_generation")
        message = status.user_message.lower()
        
        # Should mention quota
        assert "quota" in message
        # Should confirm system is correctly configured
        assert "correctly configured" in message or "will resume" in message

    def test_config_message_prompts_action(self):
        """Config issue message should prompt user action."""
        manager = get_capability_manager()
        manager.report_status("image_generation", CapabilityState.NOT_CONFIGURED)
        
        status = manager.get_status("image_generation")
        message = status.user_message.lower()
        
        # Should mention configuration
        assert "api key" in message or "configure" in message or "not configured" in message


class TestCriticalDistinction:
    """
    Critical test: Verify the non-negotiable requirement.
    
    A missing external capability must NEVER invalidate a correct implementation.
    """

    def test_quota_does_not_invalidate_implementation(self):
        """CRITICAL: Quota limit must NOT be reported as implementation error."""
        manager = get_capability_manager()
        
        # Simulate quota exceeded
        manager.report_status(
            "image_generation",
            CapabilityState.QUOTA_EXCEEDED,
            message="RESOURCE_EXHAUSTED: Gemini quota exceeded"
        )
        
        status = manager.get_status("image_generation")
        global_status = manager.get_global_status()
        
        # Individual capability check
        assert status.category == StatusCategory.OPERATIONALLY_LIMITED
        assert status.category != StatusCategory.IMPLEMENTATION_INVALID
        
        # Global check
        assert global_status.overall_category == StatusCategory.OPERATIONALLY_LIMITED
        assert global_status.overall_category != StatusCategory.IMPLEMENTATION_INVALID

    def test_provider_outage_does_not_invalidate_implementation(self):
        """CRITICAL: Provider outage must NOT be reported as implementation error."""
        manager = get_capability_manager()
        
        # Simulate provider outage
        manager.report_status(
            "text_generation",
            CapabilityState.OFFLINE,
            message="Provider returned 500 error"
        )
        
        status = manager.get_status("text_generation")
        
        # Must be operational limit, NOT implementation error
        assert status.category == StatusCategory.OPERATIONALLY_LIMITED
        assert status.category != StatusCategory.IMPLEMENTATION_INVALID

    def test_implementation_valid_flag_in_api(self):
        """CRITICAL: API must indicate implementation is valid despite quota limit."""
        manager = get_capability_manager()
        manager.report_status("image_generation", CapabilityState.QUOTA_EXCEEDED)
        
        response = manager.to_api_response()
        
        # The implementation MUST be reported as valid
        assert response["overall"]["is_implementation_valid"] is True
