"""
Configuration module for the Future Self Simulator.
Supports Azure OpenAI and standard OpenAI backends.
Priority: Azure OpenAI > OpenAI
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Standard OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # Gemini (optional)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")

    @property
    def use_azure(self) -> bool:
        """True when valid Azure OpenAI credentials are present."""
        return bool(
            self.AZURE_OPENAI_API_KEY
            and self.AZURE_OPENAI_ENDPOINT
            and "your-" not in self.AZURE_OPENAI_API_KEY
            and "your-" not in self.AZURE_OPENAI_ENDPOINT
        )

    @property
    def use_gemini(self) -> bool:
        """True when Gemini configuration is present (optional)."""
        return bool(
            self.GEMINI_API_KEY
            and self.GEMINI_BASE_URL
            and "your-" not in self.GEMINI_API_KEY
        )

    @property
    def use_openai(self) -> bool:
        """True when a standard OpenAI API key is present."""
        return bool(self.OPENAI_API_KEY and "your-" not in self.OPENAI_API_KEY)

    @property
    def is_configured(self) -> bool:
        """True when any backend is ready to use."""
        return self.use_azure or self.use_openai


settings = Settings()
