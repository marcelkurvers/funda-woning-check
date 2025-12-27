import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from backend.ai.ai_authority import AIAuthority, NoAvailableAIProviderError, ProviderStatus
from backend.main import simulate_pipeline

@pytest.fixture
def clean_authority():
    """Reset AIAuthority singleton before and after test."""
    AIAuthority.reset_singleton()
    yield
    AIAuthority.reset_singleton()

@pytest.mark.asyncio
async def test_ai_authority_fail_fast_when_offline(clean_authority):
    """
    Test that resolve_runtime raises NoAvailableAIProviderError when no provider is operational.
    Fail-Fast requirement.
    """
    auth = AIAuthority()
    
    # Mock keys to be missing
    with patch.object(auth, '_load_keys') as mock_load:
        # Manually ensure internal state is empty
        auth._openai_key = None
        auth._gemini_key = None
        auth._anthropic_key = None
        auth._ollama_base_url = "http://localhost:11434" # Configured but offline
        
        # Mock operational checks to fail
        with patch.object(auth, '_check_provider_operational', new_callable=AsyncMock) as mock_check:
            # All checks return (False, ERROR/OFFLINE, reason)
            mock_check.side_effect = lambda p: (False, ProviderStatus.OFFLINE, "Connection refused")
            
            # Verify it raises explicit error instead of returning partial decision
            with pytest.raises(NoAvailableAIProviderError) as exc_info:
                await auth.resolve_runtime(force_refresh=True)
            
            # Verify payload
            decision = exc_info.value.decision
            assert decision.active_provider == "none"
            assert decision.status == ProviderStatus.OFFLINE
            assert "All providers unavailable" in decision.reasons[-1]
            assert "Configure valid API keys" in decision.resume_hint

def test_pipeline_fails_fast_on_init_failure():
    """
    Test that simulate_pipeline aborts immediately if init_ai_provider returns False.
    Patch B requirement.
    """
    run_id = "test-fail-fast-run"
    
    # Mock dependencies
    with patch('backend.main.init_ai_provider', return_value=False) as mock_init:
        with patch('backend.main.update_run') as mock_update:
            with patch('backend.api.run_status.track_error') as mock_track:
                with patch('backend.domain.app_config.build_app_config') as mock_config:
                    # Mock valid config so we pass the first check
                    mock_config.return_value.mode.value = "production" 
                    # Actually we need validate_config_for_execution to pass too
                    with patch('backend.domain.app_config.validate_config_for_execution', return_value=(True, None)):
                        
                        simulate_pipeline(run_id)
                        
                        # Verify init called
                        mock_init.assert_called_once()
                        
                        # Verify error tracking
                        mock_track.assert_called()
                        args, _ = mock_track.call_args
                        # The logger includes run_id in message, but track_error args are (run_id, msg)
                        assert "No AI provider available" in args[0] or (len(args) > 1 and "No AI provider available" in args[1])
                        
                        # Verify status update to error
                        mock_update.assert_called()
                        # call_args_list should show status="error"
                        status_updates = [call.kwargs.get('status') for call in mock_update.call_args_list if 'status' in call.kwargs]
                        assert "error" in status_updates

@pytest.mark.asyncio
async def test_api_recovers_diagnostic_info(clean_authority):
    """
    Test that get_capabilities (used by API) recovers the decision object
    even when resolve_runtime raises exception.
    Patch C requirement.
    """
    auth = AIAuthority()
    
    # Make it fail
    with patch.object(auth, 'resolve_runtime', new_callable=AsyncMock) as mock_resolve:
        # Create a mock decision for the exception
        mock_decision = MagicMock()
        mock_decision.active_provider = "none"
        mock_decision.status = ProviderStatus.OFFLINE
        
        mock_resolve.side_effect = NoAvailableAIProviderError("Fail", mock_decision)
        
        # Test get_capabilities
        caps = auth.get_capabilities()
        
        assert caps["active_provider"] == "none"
        assert caps["status"] == ProviderStatus.OFFLINE.value
