from typing import Optional

from sqlmodel import Field

from .episode_model import EpisodeBase


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    @property
    def slug(self):
        return f"/eps/{self.id}"
