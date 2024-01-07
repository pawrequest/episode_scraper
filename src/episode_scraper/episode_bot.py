from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

from aiohttp import ClientSession
from sqlmodel import SQLModel, Session, select
from loguru import logger

from .soups import MainSoup

# if TYPE_CHECKING:
#     from .episode_model import Episode, EpisodeBase

SLEEP = os.environ.get("SCRAPER_SLEEP", 60 * 10)
EP_TYPE: type[SQLModel]
MAX_DUPES = os.environ.get("MAX_DUPES", 3)


class EpisodeBot:
    def __init__(
        self,
        sql_session: Session,
        http_session: ClientSession,
        main_soup: MainSoup,
        episode_type: type[SQLModel] = None,
    ):
        global EP_TYPE
        self.session = sql_session
        self.http_session = http_session
        self.main_soup = main_soup
        if episode_type is None:
            from .episode_model import Episode

            episode_type = Episode
        EP_TYPE = episode_type

    @classmethod
    async def from_config(cls, sql_session: Session, aio_session: ClientSession) -> EpisodeBot:
        url = os.environ.get("MAIN_URL")
        main_soup = await MainSoup.from_url(url, aio_session)
        return cls(sql_session, aio_session, main_soup)

    @classmethod
    async def from_url(cls, url, sql_session: Session, http_session: ClientSession = None) -> EpisodeBot:
        http_session = http_session or ClientSession()
        main_soup = await MainSoup.from_url(url, http_session)
        return cls(sql_session, http_session, main_soup)

    async def run(self, sleep_interval: int = SLEEP) -> None:
        """Schedule scraper and writer tasks."""
        logger.info(
            f"Initialised : {self.main_soup.main_url}",
        )
        while True:
            logger.debug("Waking")
            episode_stream = self.main_soup.episode_stream(http_session=self.http_session)
            new_stream = self._filter_existing_eps(episode_stream)
            async for added in self._add(new_stream):
                yield added
            logger.debug(f"Sleeping for {sleep_interval} seconds")
            await asyncio.sleep(sleep_interval)

    async def _add(self, eps: AsyncGenerator[EP_TYPE, None]) -> AsyncGenerator[EP_TYPE, None]:
        """Add episode to session and assign gurus."""
        async for ep in eps:
            try:
                val = EP_TYPE.model_validate(ep)
                self.session.add(val)
                self.session.commit()
                logger.info(f"New Episode: {val.title} @ {ep.url}")
                yield val
            except Exception as e:
                logger.error(f"Error adding {ep.title} to session: {e}")
                # self.session.rollback() #??

    async def _filter_existing_eps(self, episodes: AsyncGenerator[EP_TYPE, None]) -> AsyncGenerator[EP_TYPE, None]:
        """Yields episodes that do not exist in db."""
        dupes = 0
        async for episode in episodes:
            if self._episode_exists(episode):
                dupes += 1
                if dupes >= MAX_DUPES:
                    break
                continue
            yield episode

    #
    # async def _filter_existing_eps(
    #     self, episodes: AsyncGenerator[EpisodeBase, None]
    # ) -> AsyncGenerator[EpisodeBase, None]:
    #     """Yields episodes that do not exist in db."""
    #     dupes = 0
    #     async for episode in episodes:
    #         if self._episode_exists(episode):
    #             dupes += 1
    #             if dupes >= MAX_DUPES:
    #                 if DEBUG:
    #                     logger.debug(f"{dupes} duplicates found, giving up")
    #                 break
    #             continue
    #         yield episode

    def _episode_exists(self, episode: EP_TYPE) -> bool:
        """Check if episode matches title and url of existing episode in db."""
        existing_episode = self.session.exec(
            select(EP_TYPE).where((EP_TYPE.url == episode.url) & (EP_TYPE.title == episode.title))
        ).first()

        return existing_episode is not None
