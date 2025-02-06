from abc import ABC, abstractmethod
from typing import List
import json
import os
from common.new_class import News

class NewsDatabase(ABC):
    """
    Abstract base class for a news database.
    """
    @abstractmethod
    def save_news(self, news_list: List[News]):
        pass

    @abstractmethod
    def get_all(self) -> List[News]:
        pass