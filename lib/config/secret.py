from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecretSettings(BaseSettings):
    """
    Sensitive settings loaded from .secrets.env.

    Args:
        DB_USER (str): Database username loaded from the environment.
        DB_PASSWORD (str): Database password loaded from the environment.
    """

    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
