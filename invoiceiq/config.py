"""Runtime configuration, loaded from environment variables with the ``IQ_`` prefix."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IQ_", env_file=".env", extra="ignore")

    approval_limit_cents: int = 500_000
    expected_tax_rate: float = 0.19
    tax_rate_tolerance: float = 0.03
    arithmetic_tolerance_cents: int = 2
    categoriser_min_confidence: float = 0.45


def get_settings() -> Settings:
    return Settings()
