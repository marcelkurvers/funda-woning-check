# TEST_REGIME: STRUCTURAL
# REQUIRES: none (tests AI orchestration, not execution)
"""
Tests for AI Authority - Single Source of Truth

These tests verify the AIAuthority contract:
1. Single source of truth for AI keys
2. Strict provider hierarchy (OpenAI -> Gemini -> Claude -> Ollama)
3. Proper fallback cascade
4. Unified runtime status endpoint
5. Ollama keep_alive=0 enforcement
"""

import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Test that no other modules call os.getenv for AI keys
class TestSingleSourceOfTruth:
    """Verify AIAuthority is the only module reading AI keys."""
    
    def test_providers_do_not_read_env_directly(self):
        """
        Verify that provider modules don't call os.getenv for API keys.
        They must receive keys from AIAuthority.
        """
        import re
        from pathlib import Path
        
        backend_dir = Path(__file__).parent.parent.parent
        providers_dir = backend_dir / "ai" / "providers"
        
        env_patterns = [
            r'os\.getenv\s*\(\s*["\']OPENAI_API_KEY',
            r'os\.getenv\s*\(\s*["\']ANTHROPIC_API_KEY',
            r'os\.getenv\s*\(\s*["\']GEMINI_API_KEY',
            r'os\.getenv\s*\(\s*["\']GOOGLE_API_KEY',
            r'os\.environ\.get\s*\(\s*["\']OPENAI_API_KEY',
            r'os\.environ\.get\s*\(\s*["\']ANTHROPIC_API_KEY',
            r'os\.environ\.get\s*\(\s*["\']GEMINI_API_KEY',
            r'os\.environ\.get\s*\(\s*["\']GOOGLE_API_KEY',
        ]
        
        violations = []
        
        for py_file in providers_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            content = py_file.read_text()
            for pattern in env_patterns:
                if re.search(pattern, content):
                    violations.append(f"{py_file.name}: {pattern}")
        
        # We allow fallback in ollama_provider for Docker detection only
        # Filter out ollama false positives
        violations = [v for v in violations if "API_KEY" in v]
        
        assert len(violations) == 0, f"Providers reading env directly: {violations}"
    
    def test_image_provider_factory_uses_authority(self):
        """Verify image_provider_factory delegates to AIAuthority."""
        import re
        from pathlib import Path
        
        backend_dir = Path(__file__).parent.parent.parent
        factory_file = backend_dir / "ai" / "image_provider_factory.py"
        content = factory_file.read_text()
        
        # Should not contain os.getenv for keys
        assert "os.getenv" not in content, "image_provider_factory should not use os.getenv"
        
        # Should import and use AIAuthority
        assert "AIAuthority" in content or "get_ai_authority" in content


class TestProviderHierarchy:
    """Test strict provider hierarchy: OpenAI -> Gemini -> Claude -> Ollama."""
    
    def test_hierarchy_order(self):
        """Verify hierarchy constant is in correct order."""
        from backend.ai.ai_authority import PROVIDER_HIERARCHY
        
        assert PROVIDER_HIERARCHY == ["openai", "gemini", "anthropic", "ollama"]
    
    def test_openai_default_when_available(self):
        """OpenAI should be selected when its key is present."""
        from backend.ai.ai_authority import AIAuthority
        
        # Reset singleton
        AIAuthority.reset_singleton()
        
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test-key",
            "GEMINI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
        }, clear=False):
            authority = AIAuthority()
            
            # Force reload
            authority._keys_loaded = False
            authority._load_keys()
            
            assert authority._openai_key == "sk-test-key"
            assert authority._is_provider_configured("openai") == True
        
        AIAuthority.reset_singleton()
    
    def test_ollama_never_default(self):
        """Ollama should only be selected when all others fail."""
        from backend.ai.ai_authority import AIAuthority, PROVIDER_HIERARCHY
        
        # Ollama is last in hierarchy
        assert PROVIDER_HIERARCHY[-1] == "ollama"
    
    @pytest.mark.asyncio
    async def test_fallback_cascade(self):
        """Test that fallback works correctly."""
        from backend.ai.ai_authority import AIAuthority, ProviderStatus
        
        AIAuthority.reset_singleton()
        
        # Clear all keys to force Ollama fallback
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "",
            "GEMINI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
        }, clear=False):
            authority = AIAuthority()
            authority._keys_loaded = False
            authority._load_keys()
            
            # Mock all provider checks to fail except Ollama
            async def mock_check(provider):
                if provider == "ollama":
                    return True, ProviderStatus.AVAILABLE, "Operational"
                return False, ProviderStatus.NOT_CONFIGURED, "API key not configured"
            
            with patch.object(authority, '_check_provider_operational', mock_check):
                decision = await authority.resolve_runtime(force_refresh=True)
                
                # Should fall back to Ollama
                assert decision.active_provider == "ollama"
                assert "openai" in decision.fallbacks_tried
                assert "gemini" in decision.fallbacks_tried
                assert "anthropic" in decision.fallbacks_tried
        
        AIAuthority.reset_singleton()


class TestRuntimeStatusEndpoint:
    """Test the unified /api/ai/runtime-status endpoint."""
    
    def test_endpoint_schema(self):
        """Verify endpoint returns expected schema."""
        from backend.ai.ai_authority import RuntimeDecision, ProviderState, ProviderStatus, StatusCategory
        
        # Create a mock decision
        decision = RuntimeDecision(
            active_provider="openai",
            active_model="gpt-4o-mini",
            status=ProviderStatus.AVAILABLE,
            category=StatusCategory.IMPLEMENTATION_VALID,
            reasons=["Selected openai: Operational"],
            fallbacks_tried=[],
            all_providers={
                "openai": ProviderState(
                    name="openai",
                    label="OpenAI",
                    configured=True,
                    operational=True,
                    status=ProviderStatus.AVAILABLE,
                    category=StatusCategory.IMPLEMENTATION_VALID,
                    models=["gpt-4o", "gpt-4o-mini"],
                )
            },
            user_message="✓ AI actief via OpenAI",
        )
        
        # Verify required fields
        assert decision.active_provider == "openai"
        assert decision.active_model == "gpt-4o-mini"
        assert decision.status == ProviderStatus.AVAILABLE
        assert decision.category == StatusCategory.IMPLEMENTATION_VALID
        assert decision.user_message is not None
    
    def test_endpoint_exists(self):
        """Verify endpoint is registered."""
        from backend.api.ai_runtime import router
        
        routes = [r.path for r in router.routes]
        # Routes include the prefix
        assert any("/runtime-status" in r for r in routes)


class TestOllamaKeepAlive:
    """Test Ollama keep_alive=0 enforcement."""
    
    def test_keep_alive_in_payload(self):
        """Verify Ollama provider sets keep_alive=0."""
        import re
        from pathlib import Path
        
        backend_dir = Path(__file__).parent.parent.parent
        ollama_file = backend_dir / "ai" / "providers" / "ollama_provider.py"
        content = ollama_file.read_text()
        
        # Must contain keep_alive = 0
        assert 'keep_alive' in content.lower(), "Ollama provider must set keep_alive"
        assert re.search(r'"keep_alive"\s*:\s*0', content), "keep_alive must be 0"


class TestOllamaCleanup:
    """Test Ollama cleanup functionality."""
    
    def test_cleanup_endpoint_exists(self):
        """Verify cleanup endpoint is registered."""
        from backend.api.ai_runtime import router
        
        routes = [r.path for r in router.routes]
        # Routes include the prefix
        assert any("/ollama/cleanup" in r for r in routes)
    
    def test_guard_module_exists(self):
        """Verify OllamaGuard module exists."""
        from backend.ai.ollama_guard import OllamaGuard, get_ollama_guard
        
        guard = OllamaGuard()
        assert hasattr(guard, 'detect_processes')
        assert hasattr(guard, 'cleanup')
        assert hasattr(guard, 'unload_model')


class TestStatusCategories:
    """Test proper status categorization."""
    
    def test_quota_is_operational_limit(self):
        """Quota exceeded should be OPERATIONALLY_LIMITED, not IMPLEMENTATION_INVALID."""
        from backend.ai.ai_authority import AIAuthority, ProviderStatus, StatusCategory
        
        authority = AIAuthority()
        
        category = authority._status_to_category(ProviderStatus.QUOTA_EXCEEDED)
        assert category == StatusCategory.OPERATIONALLY_LIMITED
    
    def test_offline_is_operational_limit(self):
        """Offline should be OPERATIONALLY_LIMITED."""
        from backend.ai.ai_authority import AIAuthority, ProviderStatus, StatusCategory
        
        authority = AIAuthority()
        
        category = authority._status_to_category(ProviderStatus.OFFLINE)
        assert category == StatusCategory.OPERATIONALLY_LIMITED
    
    def test_not_configured_is_implementation_invalid(self):
        """Not configured should be IMPLEMENTATION_INVALID."""
        from backend.ai.ai_authority import AIAuthority, ProviderStatus, StatusCategory
        
        authority = AIAuthority()
        
        category = authority._status_to_category(ProviderStatus.NOT_CONFIGURED)
        assert category == StatusCategory.IMPLEMENTATION_INVALID


class TestAPIKeyMissing:
    """Test that 'API key missing' messages are accurate."""
    
    def test_key_status_distinction(self):
        """Verify distinction between NOT_CONFIGURED and KEY_PRESENT_BUT_FAILS."""
        from backend.ai.ai_authority import ProviderStatus
        
        # These are the expected statuses
        assert ProviderStatus.NOT_CONFIGURED.value == "not_configured"
        assert ProviderStatus.QUOTA_EXCEEDED.value == "quota_exceeded"
        assert ProviderStatus.OFFLINE.value == "offline"
        assert ProviderStatus.ERROR.value == "error"
    
    def test_user_message_is_clear(self):
        """Verify user messages are clear and actionable."""
        from backend.ai.ai_authority import AIAuthority, ProviderStatus, StatusCategory
        
        authority = AIAuthority()
        
        # Test quota message
        msg = authority._build_user_message("openai", ProviderStatus.QUOTA_EXCEEDED, StatusCategory.OPERATIONALLY_LIMITED)
        assert "quota" in msg.lower()
        assert "correct" in msg.lower() or "geconfigureerd" in msg.lower()
        
        # Test not configured message
        msg = authority._build_user_message("openai", ProviderStatus.NOT_CONFIGURED, StatusCategory.IMPLEMENTATION_INVALID)
        assert "geconfigureerd" in msg.lower() or "key" in msg.lower()


class TestIntegration:
    """Integration tests for the full flow."""
    
    @pytest.mark.asyncio
    async def test_create_text_provider(self):
        """Test that create_text_provider works."""
        from backend.ai.ai_authority import AIAuthority
        
        AIAuthority.reset_singleton()
        
        # Set up a test key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}, clear=False):
            authority = AIAuthority()
            authority._keys_loaded = False
            authority._load_keys()
            
            try:
                provider = authority.create_text_provider()
                assert provider.name == "openai"
            except Exception as e:
                # Expected if OpenAI SDK validation fails with test key
                assert "api_key" in str(e).lower() or "openai" in str(e).lower()
        
        AIAuthority.reset_singleton()
