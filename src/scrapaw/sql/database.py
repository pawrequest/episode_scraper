import contextlib
import functools
import pathlib

from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import Session

from .scrapaw_config import scrapaw_settings


@functools.lru_cache
def get_db_url():
    sett = scrapaw_settings()
    logger.info(f"USING DB FILE: {sett.db_loc}")
    db_path = pathlib.Path(sett.db_loc)
    return f"sqlite:///{db_path}"


@functools.lru_cache
def engine_():
    db_url = get_db_url()
    connect_args = {"check_same_thread": False}
    return create_engine(db_url, echo=False, connect_args=connect_args)


def get_session(engine=None) -> Session:
    if engine is None:
        engine = engine_()
    with Session(engine) as session:
        yield session
    session.close()


@contextlib.contextmanager
def session_manager(engine=None):
    if engine is None:
        engine = engine_()
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        logger.error(e)
        session.rollback()
        raise
    finally:
        session.close()
# def create_db(engine=None):
#     if engine is None:
#         engine = engine_()
#     SQLModel.metadata.create_all(engine)
