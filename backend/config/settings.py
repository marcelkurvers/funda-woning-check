"""
Configuration management using Pydantic Settings.

This module defines all configurable values in the application, replacing
hardcoded values with environment-variable-driven configuration.

See docs/CONFIGURATION.md for complete documentation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from typing import Optional, Dict, Any, Type, Tuple
from pathlib import Path
import json
import sqlite3
import os

class SQLiteSettingsSource(PydanticBaseSettingsSource):
    """
    A custom settings source that loads configuration from a SQLite kv_store table.
    """
    def get_field_value(self, field_name: str, field_class_name: str) -> Tuple[Any, str, bool]:
        # This source is designed to return the whole nested dict for each section
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent.parent
        default_db = base_dir / "data" / "local_app.db"
        db_path = os.environ.get("APP_DB", str(default_db))
        
        if not os.path.exists(db_path) and db_path != ":memory:":
            # Try once more with a fallback relative path for docker environments
            if os.path.exists("data/local_app.db"):
                db_path = "data/local_app.db"
            else:
                return d

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Check if kv_store table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kv_store'")
            if not cur.fetchone():
                conn.close()
                return d
            
            # Load all keys starting with 'config.'
            cur.execute("SELECT key, value FROM kv_store WHERE key LIKE 'config.%'")
            rows = cur.fetchall()
            for row in rows:
                section_name = row['key'].replace("config.", "")
                try:
                    d[section_name] = json.loads(row['value'])
                except json.JSONDecodeError:
                    continue
            
            conn.close()
        except Exception:
            # Silently ignore DB errors during settings load (e.g. table not yet initialized)
            pass
            
        return d


class AISettings(BaseSettings):
    """AI provider configuration.

    Previously hardcoded in:
    - ollama_client.py:92 (timeout)
    - intelligence.py (provider/model selection)
    
    New fields for explicit configuration UX:
    - mode: Operating mode (fast/full/debug/offline)
    """

    provider: str = "ollama"  # ollama, openai, anthropic, gemini
    model: str = "llama3"  # Model name (provider-specific)
    mode: str = "full"  # Operating mode: fast, full, debug, offline
    timeout: int = 30  # Request timeout in seconds
    fallback_enabled: bool = True  # Fall back to hardcoded content if AI fails
    temperature: float = 0.7  # Generation temperature
    max_tokens: int = 4096  # Max response tokens

    # API keys (optional, can come from env vars)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Ollama-specific
    ollama_base_url: Optional[str] = None  # Auto-detected if not set

    model_config = SettingsConfigDict(env_prefix="AI_")


class MarketSettings(BaseSettings):
    """Market analysis configuration.

    Previously hardcoded in:
    - main.py:469 (avg_price_m2)
    - Various chapters (energy_label_scores)
    """

    avg_price_m2: int = 5200  # Average price per m² in Dutch market

    # Energy label score mapping (A-G)
    energy_label_scores: Dict[str, int] = {
        "A": 95,
        "B": 80,
        "C": 65,
        "D": 50,
        "E": 35,
        "F": 20,
        "G": 10,
    }

    model_config = SettingsConfigDict(env_prefix="MARKET_")


class FitScoreSettings(BaseSettings):
    """Fit score calculation configuration.

    Previously hardcoded in:
    - main.py:445-450
    """

    base: float = 0.50  # Base fit score
    completeness_bonus: float = 0.20  # Bonus for >80% data completeness
    energy_bonus: float = 0.15  # Bonus for A/B energy label

    model_config = SettingsConfigDict(env_prefix="FIT_SCORE_")


class ValidationSettings(BaseSettings):
    """Parser validation limits.

    Previously hardcoded in:
    - parser.py (various validation thresholds)
    """

    # Bedroom/bathroom limits
    max_bedrooms: int = 15
    max_bathrooms: int = 10
    max_total_rooms: int = 30

    # Area limits (m²)
    min_living_area: int = 10
    max_living_area: int = 2000

    # Build year limits
    min_build_year: int = 1500
    max_build_year: int = 2030

    model_config = SettingsConfigDict(env_prefix="VALIDATION_")


class PipelineSettings(BaseSettings):
    """Pipeline execution settings.

    Previously hardcoded in:
    - main.py:180 (max_workers)
    - main.py:270 (image_max_size_mb)
    - App.tsx:103 (poll_interval_ms - frontend reference only)
    """

    max_workers: int = 10  # ThreadPoolExecutor max workers
    image_max_size_mb: int = 10  # Maximum upload file size
    poll_interval_ms: int = 2000  # Frontend status poll interval (reference)

    model_config = SettingsConfigDict(env_prefix="PIPELINE_")


class UserPreferencesSettings(BaseSettings):
    """User preferences configuration (Marcel & Petra profiles).

    These provide default values. Runtime preferences are stored in
    SQLite `kv_store` table under key `preferences`.
    """

    # Marcel's profile defaults
    marcel_keywords: list[str] = ["glasvezel", "zonnepanelen", "garage", "laadpaal", "1930"]
    marcel_tech_weight: float = 0.4
    marcel_infrastructure_weight: float = 0.3
    marcel_energy_weight: float = 0.3
    marcel_hidden_priorities: list[str] = ["bouwjaar", "dakisolatie"]

    # Petra's profile defaults
    petra_keywords: list[str] = ["karakteristiek", "sfeer", "tuin", "bad", "licht"]
    petra_atmosphere_weight: float = 0.4
    petra_comfort_weight: float = 0.3
    petra_finish_weight: float = 0.3
    petra_hidden_priorities: list[str] = ["afwerking", "badkamer"]

    model_config = SettingsConfigDict(env_prefix="PREF_")


class ChapterSettings(BaseSettings):
    """Chapter titles and configuration.

    Previously hardcoded in:
    - main.py:68-82
    """

    titles: Dict[str, str] = {
        "0": "Introductie & Samenvatting",
        "1": "Algemene Woningkenmerken",
        "2": "Matchanalyse Marcel & Petra",
        "3": "Bouwkundige Staat",
        "4": "Energie & Duurzaamheid",
        "5": "Indeling & Ruimtegebruik",
        "6": "Onderhoud & Afwerking",
        "7": "Tuin & Buitenruimte",
        "8": "Parkeren & Bereikbaarheid",
        "9": "Juridische Aspecten",
        "10": "Financiële Analyse",
        "11": "Marktpositie",
        "12": "Advies & Conclusie",
    }

    model_config = SettingsConfigDict(env_prefix="CHAPTER_")


class AppSettings(BaseSettings):
    """Main application settings.

    Aggregates all configuration domains and provides a single entry point
    for accessing configuration values throughout the application.

    Configuration precedence (highest to lowest):
    1. Environment variables
    2. SQLite `kv_store` table (runtime changes)
    3. .env file (development defaults)
    4. Class defaults (code fallback)
    """

    # Nested configuration domains
    ai: AISettings = AISettings()
    market: MarketSettings = MarketSettings()
    fit_score: FitScoreSettings = FitScoreSettings()
    validation: ValidationSettings = ValidationSettings()
    pipeline: PipelineSettings = PipelineSettings()
    preferences: UserPreferencesSettings = UserPreferencesSettings()
    chapters: ChapterSettings = ChapterSettings()

    # Database configuration
    database_url: str = str(Path(__file__).resolve().parent.parent.parent / "data" / "local_app.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # Allows AI__TIMEOUT env var syntax
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            SQLiteSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


# Singleton instance for application-wide configuration access
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get application settings (singleton pattern).

    Returns:
        AppSettings: The global settings instance

    Example:
        ```python
        from config.settings import get_settings

        settings = get_settings()
        timeout = settings.ai.timeout
        avg_price = settings.market.avg_price_m2
        ```
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reset_settings():
    """Reset settings singleton (for testing).

    This allows tests to reload settings with different environment
    variables or .env file contents.

    Example:
        ```python
        # In test setup
        import os
        from config.settings import reset_settings, get_settings

        os.environ["AI_TIMEOUT"] = "60"
        reset_settings()
        settings = get_settings()
        assert settings.ai.timeout == 60
        ```
    """
    global _settings
    _settings = None
