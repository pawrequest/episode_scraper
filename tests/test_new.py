import asyncio
from asyncio import Queue

import aiohttp
import pytest
import pytest_asyncio

from scraper.episode import EpisodeDC
from scraper.implementations.dtg_scraper import DTGScraper


@pytest_asyncio.fixture
async def scraper_fxt():
    async with aiohttp.ClientSession() as http_session:
        yield DTGScraper("https://decoding-the-gurus.captivate.fm/", http_session)


@pytest.mark.asyncio
async def test_scraper(scraper_fxt):
    assert isinstance(scraper_fxt, DTGScraper)


@pytest.mark.asyncio
async def test_scraper_run(scraper_fxt):
    task = asyncio.create_task(scraper_fxt.go())
    ep = await scraper_fxt.queue.get()
    assert isinstance(ep, EpisodeDC)
    task.cancel()
    await asyncio.gather(task)


@pytest.mark.asyncio
async def test_scraper_go_gen(scraper_fxt):
    async for ep in scraper_fxt.go():
        assert isinstance(ep, EpisodeDC)
        break
