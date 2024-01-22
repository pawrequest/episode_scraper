import asyncio
from asyncio import Queue

import aiohttp
import pytest
import pytest_asyncio

from episode_scraper.episode import EpisodeDC
from episode_scraper.dtg import DTGScraper


@pytest_asyncio.fixture
async def scraper_fxt():
    async with aiohttp.ClientSession() as http_session:
        yield DTGScraper("https://decoding-the-gurus.captivate.fm/", http_session, Queue())


@pytest.mark.asyncio
async def test_scraper(scraper_fxt):
    assert isinstance(scraper_fxt, DTGScraper)


@pytest.mark.asyncio
async def test_scraper_run(scraper_fxt):
    task = asyncio.create_task(scraper_fxt.run())
    ep = await scraper_fxt.queue.get()
    assert isinstance(ep, EpisodeDC)
    task.cancel()
    await asyncio.gather(task)
