from abc import ABC, abstractmethod
from datetime import datetime

class AbstractNewsScraper(ABC):
    def __init__(self, source: str):
        self.source = source
    @abstractmethod
    def scrape_time_interval(self,start_date: str, end_date: str):
        pass