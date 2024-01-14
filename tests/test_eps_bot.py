import asyncio
import os

import pytest
import pytest_asyncio
from aiohttp import ClientSession
from sqlmodel import SQLModel, Session, create_engine, select

from episode_scraper.episode_bot import EpisodeBot
from episode_scraper.episode_db_model import Episode


@pytest.fixture(scope="session")
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


MAIN_URL = "https://decoding-the-gurus.captivate.fm"


@pytest_asyncio.fixture
async def episode_bot(session):
    return await EpisodeBot.from_url(MAIN_URL, session)


@pytest.mark.asyncio
async def test_episode_bot_initialization(episode_bot):
    assert isinstance(episode_bot, EpisodeBot)


@pytest.mark.asyncio
async def test_gets_episodes_and_skip_existing(episode_bot, session):
    e1 = await anext(episode_bot.run())
    eps = session.exec(select(Episode)).all()
    assert e1 in eps
    e2 = await anext(episode_bot.run())
    assert e2 != e1


@pytest.mark.asyncio
async def test_uses_queue(episode_bot: EpisodeBot):
    tasks = []
    episode_q = asyncio.Queue()
    tasks.append(asyncio.create_task(episode_bot.run_q(episode_q)))
    tasks.append(asyncio.create_task(process_episodes(episode_q)))
    for _ in range(2):
        ep = await episode_q.get()
        assert ep.title

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def process_episodes(queue: asyncio.Queue):
    while True:
        result = await queue.get()
        print(result.title)
        queue.task_done()
