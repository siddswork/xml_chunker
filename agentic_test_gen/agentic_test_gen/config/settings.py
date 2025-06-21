"""
Configuration settings for the agentic XSLT test generator.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelSettings:
    """Model configuration settings."""
    o4_mini_model: str = "o1-mini"  # Actual OpenAI model name
    gpt41_model: str = "gpt-4-turbo-preview"  # Actual OpenAI model name
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout_seconds: int = 60


@dataclass
class PerformanceSettings:
    """Performance and resource settings."""
    max_concurrent_agents: int = 3
    analysis_timeout: int = 300
    cache_ttl: int = 86400  # 24 hours
    max_retries: int = 3


@dataclass
class QualitySettings:
    """Quality thresholds and requirements."""
    min_test_cases: int = 125
    min_business_rules: int = 45
    min_pattern_coverage: float = 0.95
    max_analysis_time_minutes: int = 30


@dataclass
class AgenticSystemSettings:
    """Main configuration for the agentic system."""
    
    # API Configuration
    openai_api_key: Optional[str] = None
    
    # Model Settings
    model: ModelSettings = ModelSettings()
    
    # Performance Settings
    performance: PerformanceSettings = PerformanceSettings()
    
    # Quality Settings
    quality: QualitySettings = QualitySettings()
    
    # Storage Settings
    knowledge_base_path: str = "knowledge_base.json"
    cache_directory: str = "cache"
    logs_directory: str = "logs"
    
    # Debug Settings
    debug_mode: bool = False
    verbose_logging: bool = False
    
    def __post_init__(self):
        """Initialize settings from environment variables."""
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Override with environment variables if available
        if os.getenv("DEBUG"):
            self.debug_mode = os.getenv("DEBUG").lower() == "true"
        
        if os.getenv("VERBOSE"):
            self.verbose_logging = os.getenv("VERBOSE").lower() == "true"


def get_settings() -> AgenticSystemSettings:
    """Get the global settings instance."""
    return AgenticSystemSettings()


def validate_settings(settings: AgenticSystemSettings) -> None:
    """Validate settings configuration."""
    if not settings.openai_api_key:
        raise ValueError(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass explicitly."
        )
    
    if settings.quality.min_test_cases < 1:
        raise ValueError("Minimum test cases must be at least 1")
    
    if settings.quality.min_pattern_coverage < 0.0 or settings.quality.min_pattern_coverage > 1.0:
        raise ValueError("Pattern coverage must be between 0.0 and 1.0")