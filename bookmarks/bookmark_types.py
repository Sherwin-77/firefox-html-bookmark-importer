from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TypedDict, Union


@dataclass
class Bookmark:
    name: str
    url: str


@dataclass
class BookmarkFolder:
    name: str
    items: List[Union[Bookmark, BookmarkFolder]] = field(default_factory=list)


class BookmarkInfo(TypedDict):
    url: Optional[str]
    type: int
    root_id: int
    parent_guid: str
    title: str
    position: Optional[int]
    date_added: int
    last_modified: int
    guid: str
    syncStatus: int
    syncChangeCounter: int


BookmarkTree = List[Union[Bookmark, BookmarkFolder]]