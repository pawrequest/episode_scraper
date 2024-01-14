from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

from aiohttp import ClientSession
from sqlmodel import SQLModel, Session, select
from loguru import logger

from .soups import MainSoup

# global to allow extending episodebase in client app, else fallback to Episode in this package for standalone
# must be a better way but many import errors and table collisions were had and this seems to work
EPISODE_TYPE: type[SQLModel]

SLEEP = os.environ.get("SCRAPER_SLEEP", 60 * 10)
MAX_DUPES = os.environ.get("MAX_DUPES", 3)


def set_episode_type(episode_db_type: type[SQLModel] = None):
    if episode_db_type is None:
        logger.info("Using default Episode model")
        from .episode_db_model import Episode

        episode_db_type = Episode
    global EPISODE_TYPE
    EPISODE_TYPE = episode_db_type


class EpisodeBot:
    def __init__(
        self,
        sql_session: Session,
        http_session: ClientSession,
        main_soup: MainSoup,
        episode_db_type: type[SQLModel] = None,
    ):
        self.session = sql_session
        self.http_session = http_session
        self.main_soup = main_soup

        set_episode_type(episode_db_type)

    @classmethod
    async def from_config(
        cls, sql_session: Session, aio_session: ClientSession, episode_db_type: SQLModel = None
    ) -> "EpisodeBot":
        url = os.environ.get("MAIN_URL")
        main_soup = await MainSoup.from_url(url, aio_session)
        return cls(sql_session, aio_session, main_soup, episode_db_type)

    @classmethod
    async def from_url(
        cls, url, sql_session: Session, http_session: ClientSession = None, episode_db_type: type[SQLModel] = None
    ) -> "EpisodeBot":
        http_session = http_session or ClientSession()
        main_soup = await MainSoup.from_url(url, http_session)
        return cls(sql_session, http_session, main_soup, episode_db_type)

    async def run_q(self, queue: asyncio.Queue, sleep_interval: int = SLEEP) -> None:
        """Schedule scraper and writer tasks."""
        logger.info(
            f"Initialised : {self.main_soup.main_url}",
        )
        while True:
            logger.debug("Waking")
            episode_stream = self.main_soup.episode_stream(http_session=self.http_session)
            new_stream = self._filter_existing_eps(episode_stream)
            async for added in self._add(new_stream):
                await queue.put(added)
            logger.debug(f"Sleeping for {sleep_interval} seconds")
            await asyncio.sleep(sleep_interval)

    async def _add(self, eps: AsyncGenerator[EPISODE_TYPE, None]) -> AsyncGenerator[EPISODE_TYPE, None]:
        """Add episode to session and assign gurus."""
        async for ep in eps:
            try:
                val = EPISODE_TYPE.model_validate(ep)
                self.session.add(val)
                self.session.commit()
                logger.info(f"New Episode: {val.title} @ {ep.url}")
                yield val
            except Exception as e:
                logger.error(f"Error adding {ep.title} to session: {e}")
                # self.session.rollback() #??

    async def _filter_existing_eps(
        self, episodes: AsyncGenerator[EPISODE_TYPE, None]
    ) -> AsyncGenerator[EPISODE_TYPE, None]:
        """Yields episodes that do not exist in db."""
        dupes = 0
        async for episode in episodes:
            if self._episode_exists(episode):
                dupes += 1
                if dupes >= MAX_DUPES:
                    break
                continue
            yield episode

    def _episode_exists(self, episode: EPISODE_TYPE) -> bool:
        """Check if episode matches title and url of existing episode in db."""
        existing_episode = self.session.exec(
            select(EPISODE_TYPE).where((EPISODE_TYPE.url == episode.url) & (EPISODE_TYPE.title == episode.title))
        ).first()

        return existing_episode is not None
