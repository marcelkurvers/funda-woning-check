from typing import Dict, Type
from chapters.base import BaseChapter
from chapters.chapter_0 import ExecutiveSummary
from chapters.definitions import (
    Chapter1, Chapter2, Chapter3, Chapter4, Chapter5, Chapter6, 
    Chapter7, Chapter8, Chapter9, Chapter10, Chapter11, Chapter12
)

_REGISTRY: Dict[int, Type[BaseChapter]] = {
    0: ExecutiveSummary,
    1: Chapter1,
    2: Chapter2,
    3: Chapter3,
    4: Chapter4,
    5: Chapter5,
    6: Chapter6,
    7: Chapter7,
    8: Chapter8,
    9: Chapter9,
    10: Chapter10,
    11: Chapter11,
    12: Chapter12,
}

def get_chapter_class(chapter_id: int) -> Type[BaseChapter]:
    return _REGISTRY.get(chapter_id)
