from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    telegram_bot_token: str = Field(default='')
    openai_api_key: str = Field(default='')
    openai_base_url: str = Field(default='https://openrouter.ai/api/v1')
    openai_model: str = Field(default='openai/gpt-4o-mini')
    dashboard_password: str = Field(default='bitte_aendern')

    storage_mode: str = Field(default='json')
    data_dir: str = Field(default='data')
    supabase_url: str = Field(default='')
    supabase_service_key: str = Field(default='')
    supabase_anon_key: str = Field(default='')

    smtp_host: str = Field(default='')
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default='')
    smtp_password: str = Field(default='')
    smtp_from: str = Field(default='')
    smtp_use_tls: bool = Field(default=True)
    imap_host: str = Field(default='')
    imap_port: int = Field(default=993)
    imap_user: str = Field(default='')
    imap_password: str = Field(default='')

    search_provider: str = Field(default='mock')
    brave_search_api_key: str = Field(default='')
    serper_api_key: str = Field(default='')
    firecrawl_api_key: str = Field(default='')

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
