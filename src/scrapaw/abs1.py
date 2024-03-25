# import abc
# import datetime as dt
# import inspect
# import typing as _t
#
# import aiohttp
# import pydantic as _p
# from dateutil import parser
#
# from scrapaw.consts import MAX_DUPES
#
#
# class Episode(_p.BaseModel):
#     title: str
#     url: str
#     date: dt.date
#     notes: list[str]
#     links: dict[str, str]
#     number: str
#
#     @classmethod
#     @abc.abstractmethod
#     async def from_url(cls, url, session: aiohttp.ClientSession | None = None) -> _t.Self:
#         raise NotImplementedError
#
#     @_p.field_validator('date', mode='before')
#     def date_is_str(cls, v):
#         if isinstance(v, str):
#             res = parser.parse(v).date()
#             print(f'Parsed date: {v} - to - {res}')
#             return res
#         return v
#
#     @_p.field_validator("number", mode="before")
#     def ep_number_is_str(cls, v) -> str:
#         return str(v)
#
#     def log_str(self) -> str:
#         if self.title and self.date:
#             return f"\t\t<green>{self.date}</green> - <bold><cyan>{self.title}</cyan></bold>"
#         else:
#             return f"\t\t{self.url}"
#
#     def __str__(self):
#         return f"{self.__class__.__name__}: {self.title or self.url}"
#
#     # def __repr__(self):
#     #     return f"<{self.__class__.__name__}({self.url})>"
#
#     @classmethod
#     def log_episodes(cls, eps: _t.Sequence[_t.Self], calling_func=None, msg: str = ""):
#         """Logs the first 3 episodes and the last 2 episodes of a sequence episodes"""
#         if not eps:
#             return
#         if calling_func:
#             calling_f = calling_func.__name__
#         else:
#             calling_f = f"{inspect.stack()[1].function} INSPECTED, YOU SHOULD PROVIDE THE FUNC"
#
#         new_msg = f"{msg} {len(eps)} Episodes in {calling_f}():\n"
#         new_msg += episodes_log_msg(eps)
#         print(new_msg)
#
#
# def episodes_log_msg(eps: _t.Sequence[Episode]) -> str:
#     msg = ""  # in case no eps
#     msg += "\n".join([_.log_str() for _ in eps[:3]])
#
#     if len(eps) == 4:
#         fth = eps[3]
#         msg += f"\n{fth.log_str()}"
#     elif len(eps) > 4:
#         to_log = min([2, abs(len(eps) - 4)])
#         msg += " \n\t... more ...\n"
#         msg += "\n".join([_.log_str() for _ in eps[-to_log:]])
#     return msg
#
#
# class Podcast(_p.BaseModel, abc.ABC):
#     name: _t.ClassVar[str]
#     base_url: _t.ClassVar[str]
#     episodes: list[Episode] = _p.Field(default_factory=list)
#
#     async def all_urls(self) -> list[str]:
#         raise NotImplementedError
#
#     @abc.abstractmethod
#     async def get_episodes(
#             self,
#             limit: int | None = None,
#             session: aiohttp.ClientSession | None = None,
#             max_dupes: int = 3
#     ):
#         raise NotImplementedError
#
#
# class DupeError(Exception):
#     ...
#
#
# class MaxDupeError(Exception):
#     ...
#
#
# async def dupes_not_exceeded(dupes):
#     if dupes > MAX_DUPES:
#         raise MaxDupeError(f"Found {dupes} duplicates, stopping")
