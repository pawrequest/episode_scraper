import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl

SCRAPAW_ENV = os.getenv("SCRAPAW_ENV")
print()
if not SCRAPAW_ENV or not Path(SCRAPAW_ENV).exists():
    raise ValueError(f"GURU_ENV ({SCRAPAW_ENV}) not set or file missing")


class ScrapawConfig(BaseSettings):
    db_loc: Path
    log_file: Path
    podcast_url: HttpUrl

    max_dupes: int = 10
    debug: bool = False
    scrape_limit: int | None = None

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=SCRAPAW_ENV)


@lru_cache
def scrapaw_settings():
    return ScrapawConfig()
