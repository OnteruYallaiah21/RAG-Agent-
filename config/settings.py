"""
===========================================================
Project: Agents-Rag
Developer: Yallaiah Onteru
Contact: yonteru414@gmail.com | GitHub: @https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/ 
Support: yonteru.ai.engineer@gmail.com
===========================================================

Description:
------------
Configuration management for AI Agents with LangChain and multiple AI providers.
Loads environment variables and provides centralized configuration.

Main Use:
---------
Centralized configuration management that:
1. Loads environment variables from .env file
2. Validates AI provider configurations
3. Provides settings for all system components
4. Manages web server settings
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Centralized configuration settings with Pydantic validation."""
    
    # AI Provider API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    groq_api_key: Optional[str] = Field(None, env="GROQ_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Google Services
    google_sheets_credentials: Optional[str] = Field(None, env="GOOGLE_SHEETS_CREDENTIALS")
    sheet_id: Optional[str] = Field(None, env="SHEET_ID")
    
    
    # Web Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(5000, env="PORT")  # Changed to port 5000
    debug: bool = Field(False, env="DEBUG")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("data/logs.txt", env="LOG_FILE")
    
    # AI Model Configuration
    default_model: str = Field("gpt-3.5-turbo", env="DEFAULT_MODEL")
    max_tokens: int = Field(2000, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    
    # Streaming Configuration
    enable_streaming: bool = Field(True, env="ENABLE_STREAMING")
    stream_chunk_size: int = Field(100, env="STREAM_CHUNK_SIZE")
    
    # Security
    secret_key: str = Field("your-secret-key-change-this", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    
    # Google Sheets Configuration
    sheet_range: str = Field("Sheet1!A:F", env="SHEET_RANGE")
    
    # Available AI Providers
    available_providers: List[str] = Field(
        default=["openai", "groq", "google", "anthropic"],
        env="AVAILABLE_PROVIDERS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields to prevent validation errors
    
    def get_ai_provider_config(self, provider: str) -> dict:
        """Get configuration for specific AI provider."""
        # =============== start get_ai_provider_config ======
        configs = {
            "openai": {
                "api_key": self.openai_api_key,
                "model": "gpt-3.5-turbo",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            },
            "groq": {
                "api_key": self.groq_api_key,
                "model": "llama3-8b-8192",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            },
            "google": {
                "api_key": self.google_api_key,
                "model": "gemini-pro",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            },
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "model": "claude-3-sonnet-20240229",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        }
        return configs.get(provider, {})
    
    def validate_ai_providers(self) -> List[str]:
        """Validate which AI providers have valid API keys."""
        # =============== start validate_ai_providers ======
        valid_providers = []
        for provider in self.available_providers:
            config = self.get_ai_provider_config(provider)
            if config.get("api_key"):
                valid_providers.append(provider)
        return valid_providers
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific AI provider is available."""
        # =============== start is_provider_available ======
        return provider in self.validate_ai_providers()

# Global settings instance
settings = Settings()
