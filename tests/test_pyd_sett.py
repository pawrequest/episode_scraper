from pathlib import Path

import pytest

from DTGBot.guru_config import dtgb_sett


def test_pyd_sett():
    sett = dtgb_sett()
    assert sett
    assert Path(sett.db_loc).exists()


@pytest.mark.asyncio
async def test_get_add_to_session():
    ...
