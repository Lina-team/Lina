import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(ConfigBase):
    model_config = SettingsConfigDict()

    bot_token: str
    db_url: str


config = Config()
