import pytest
from unittest.mock import AsyncMock, patch
from backend.ai.ai_authority import AIAuthority, ProviderStatus
from backend.ai.providers.openai_provider import OpenAIProvider

@pytest.fixture
def clean_authority():
    """Reset AIAuthority singleton before and after test."""
    AIAuthority.reset_singleton()
    yield
    AIAuthority.reset_singleton()

@pytest.mark.asyncio
async def test_resolve_runtime_selects_openai_when_key_set(clean_authority):
    """
    Test that resolve_runtime prioritizes OpenAI when configured and operational.
    """
    auth = AIAuthority()
    
    # Mock checks
    with patch.object(auth, '_load_keys') as mock_load:
        auth._openai_key = "sk-test-key"
        auth._gemini_key = None
        
        with patch.object(auth, '_check_provider_operational', new_callable=AsyncMock) as mock_check:
            # OpenAI is operational
            def side_effect(provider):
                if provider == "openai":
                    return (True, ProviderStatus.AVAILABLE, "Operational")
                return (False, ProviderStatus.NOT_CONFIGURED, "Not configured")
            
            mock_check.side_effect = side_effect
            
            decision = await auth.resolve_runtime(force_refresh=True)
            
            assert decision.active_provider == "openai"
            assert decision.active_model == "gpt-4o-mini"
            assert decision.status == ProviderStatus.AVAILABLE

@pytest.mark.asyncio
async def test_resolve_runtime_avoids_ollama_if_openai_online(clean_authority):
    """
    Test that Ollama is NOT selected if OpenAI is available, even if Ollama is also online.
    Strict hierarchy enforcement.
    """
    auth = AIAuthority()
    
    with patch.object(auth, '_load_keys') as mock_load:
        auth._openai_key = "sk-test-key"
        auth._ollama_base_url = "http://localhost:11434"
        
        with patch.object(auth, '_check_provider_operational', new_callable=AsyncMock) as mock_check:
            # Both operational
            mock_check.return_value = (True, ProviderStatus.AVAILABLE, "Operational")
            
            decision = await auth.resolve_runtime(force_refresh=True)
            
            # OpenAI is higher in hierarchy (index 0 vs index 3)
            assert decision.active_provider == "openai"
            assert decision.active_provider != "ollama"

@pytest.mark.asyncio
async def test_openai_json_compatibility_swap():
    """
    Test that OpenAIProvider swaps incompatible model to gpt-4o when json_mode is True.
    """
    provider = OpenAIProvider(api_key="test", model="gpt-4") # Legacy model
    
    with patch.object(provider.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value.choices[0].message.content = "{}"
        
        await provider.generate("prompt", json_mode=True)
        
        # Verify call arguments
        call_kwargs = mock_create.call_args.kwargs
        
        # Should have swapped to gpt-4o because gpt-4 doesn't support json_mode
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["response_format"] == {"type": "json_object"}

@pytest.mark.asyncio
async def test_openai_no_swap_needed():
    """
    Test that OpenAIProvider keeps compatible model.
    """
    provider = OpenAIProvider(api_key="test", model="gpt-4o-mini") # Compatible
    
    with patch.object(provider.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value.choices[0].message.content = "{}"
        
        await provider.generate("prompt", json_mode=True)
        
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o-mini"
        assert call_kwargs["response_format"] == {"type": "json_object"}
