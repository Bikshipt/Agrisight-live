"""
Configuration settings for the backend.
Expected env vars: MOCK_GEMINI, RATE_LIMIT_PER_MINUTE
Testing tips: Override these in tests using monkeypatch.
"""
import os

class Settings:
    MOCK_GEMINI: bool = os.getenv("MOCK_GEMINI", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

settings = Settings()
