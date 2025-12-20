"""
Configuration package for AI Woning Rapport.

This package provides centralized configuration management using Pydantic Settings,
replacing hardcoded values throughout the application with environment-variable-driven
configuration.

Public API:
    get_settings() -> AppSettings: Get the global settings instance
    reset_settings(): Reset settings singleton (for testing)
    AppSettings: Main settings class (for type hints)

Usage:
    ```python
    from config import get_settings

    settings = get_settings()
    timeout = settings.ai.timeout
    avg_price = settings.market.avg_price_m2
    max_bedrooms = settings.validation.max_bedrooms
    ```

See Also:
    docs/CONFIGURATION.md - Complete configuration reference
"""

from .settings import get_settings, reset_settings, AppSettings

__all__ = ["get_settings", "reset_settings", "AppSettings"]
