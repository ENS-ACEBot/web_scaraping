from abc import ABC, abstractmethod
from typing import List
import json
import os
from new_class import News

class NewsDatabase(ABC):
    """
    Abstract base class for a news database.
    """
    @abstractmethod
    def save_news(self, news_list: List[News]):
        """_summary_
            save a list of news to the database
        Args:
            news_list (List[News]): a list of news instances to save
        """
        pass
    abstractmethod
    def save_new(self,news : News):
        """_summary_
            save a single news to the database
        Args:
            news (News): a single news instance to save
        """
        pass
    @abstractmethod
    def get_all(self) -> list[News]:
        """_summary_
            get all news from the database
        Returns:
            list[News]: a list of news
        """
        pass
    
    @abstractmethod
    def get_query(self, from_date: str = None, to_date: str = None, source: str = None,limit: int=None) -> list[News]:
        """_summary_
            get news from the database based on query parameters
        Args:
            from_date (str, optional): _description_. Defaults to None.
            to_date (str, optional): _description_. Defaults to None.
            source (str, optional): _description_. Defaults to None.
            limit (int, optional): _description_. Defaults to None.
        Returns:
            list[News]: _description_
        """
        pass
    
    @abstractmethod
    def count_rows(self) -> int:
        """_summary_
            count the number of rows in the database
        Returns:
            int: count of rows
        """
        pass
    
    @abstractmethod
    def create_table(self):
        pass
