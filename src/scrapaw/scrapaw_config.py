import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl


class ScrapawConfig(BaseSettings):
    log_file: Path
    podcast_url: HttpUrl

    max_dupes: int = 10
    debug: bool = False
    scrape_limit: int | None = None

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=os.getenv("SCRAPAW_ENV"))


@lru_cache
def scrapaw_sett():
    return ScrapawConfig()
