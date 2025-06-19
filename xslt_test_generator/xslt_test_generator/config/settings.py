"""Configuration management for XSLT Test Generator."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """LLM configuration settings."""
    model: str
    temperature: float = 0.3
    max_tokens: int = 4000

class AgentConfig(BaseModel):
    """Agent configuration settings."""
    role: str
    goal: str
    verbose: bool = True
    max_retries: int = 2

class OutputConfig(BaseModel):
    """Output configuration settings."""
    format: str = "gherkin"
    file_extension: str = ".feature"
    include_metadata: bool = True

class EvaluationConfig(BaseModel):
    """Evaluation configuration settings."""
    enabled: bool = True
    metrics: list[str] = ["relevancy", "coherence", "completeness"]
    threshold: float = 0.7

class Settings(BaseModel):
    """Application settings."""
    
    # API Keys
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    google_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    deepeval_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("DEEPEVAL_API_KEY"))
    
    # Application Settings
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    output_dir: str = Field(default_factory=lambda: os.getenv("OUTPUT_DIR", "./output"))
    
    # Configuration from YAML
    llm: Dict[str, Any] = {}
    agents: Dict[str, AgentConfig] = {}
    output: OutputConfig = OutputConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    
    @classmethod
    def load_from_yaml(cls, config_path: Path = None) -> "Settings":
        """Load settings from YAML configuration file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Parse agent configurations
        agents = {}
        if 'agents' in config_data:
            for agent_name, agent_data in config_data['agents'].items():
                agents[agent_name] = AgentConfig(**agent_data)
        
        # Parse output configuration
        output = OutputConfig()
        if 'output' in config_data:
            output = OutputConfig(**config_data['output'])
        
        # Parse evaluation configuration
        evaluation = EvaluationConfig()
        if 'evaluation' in config_data:
            evaluation = EvaluationConfig(**config_data['evaluation'])
        
        return cls(
            llm=config_data.get('llm', {}),
            agents=agents,
            output=output,
            evaluation=evaluation
        )
    
    def get_llm_config(self, provider: str = None) -> LLMConfig:
        """Get LLM configuration for specified provider."""
        if provider is None:
            provider = self.llm.get('default_provider', 'openai')
        
        if provider not in self.llm.get('models', {}):
            raise ValueError(f"LLM provider '{provider}' not configured")
        
        model_config = self.llm['models'][provider]
        return LLMConfig(**model_config)

# Global settings instance
settings = Settings.load_from_yaml()