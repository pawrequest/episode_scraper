from pathlib import Path

import pytest

from DecodeTheBot.models.episode_m import Episode
from scrapaw.sql.episode_sql import get_add_to_session
from scrapaw.sql.scrapaw_config import scrapaw_settings


def test_pyd_sett():
    sett = scrapaw_settings()
    assert sett
    assert Path(sett.db_loc).exists()


@pytest.mark.asyncio
async def test_get_add_to_session():
    await get_add_to_session(Episode)
