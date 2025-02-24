from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    disabled_genres_create: Optional[List[str]] = ["Horror"]
    disabled_genres_search: Optional[List[str]] = ["18+"]
    masked_genres: Optional[List[str]] = ["18+"]


settings = Settings()
