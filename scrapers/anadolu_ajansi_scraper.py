import requests
import logging
from datetime import datetime,timedelta
from common.new_class import News
from scrapers.abstract_news_scraper import AbstractNewsScraper

class AnadoluAjansiScraper(AbstractNewsScraper):
    """
    A scraper for fetching and processing news from Anadolu Ajansı.
    There is no historical data available, so the scraper can only fetch news for the current date or maybe 1 day before.
    """

    def __init__(self):
        """
        Initialize the scraper with base URL and source name.
        """
        self.base_url = "https://www.aa.com.tr/tr/ekonomi"
        super().__init__("ANADOLU_AJANSI")  # self.source = "ANADOLU_AJANSI"

    def scrape_time_interval(self, start_date: str, end_date: str) -> list[News]:
        """
        Main method to scrape news data for the date range.
        date_format='%Y-%m-%d'
        """
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # fetch the news_link from the page for given interval
        filtered_news = []
        num_first = 1
        num_fin = 5

        while True:
            news_list = self.fetch_news(num_first, num_fin)
            logging.debug(f"[Anadolu Ajansı] Fetched {len(news_list)} news articles.")
            if not news_list:
                break
            
            
            for news in news_list:
                news_date = datetime.strptime(news['StartDate'], '%d.%m.%Y').date()
                logging.debug(f"[Anadolu Ajansı] News date: {news_date}")
                if start_date <= news_date <= end_date:
                    filtered_news.append(news)
                elif news_date < start_date:
                    break

            num_first += 5

        logging.debug(f"[Anadolu Ajansı] Found {len(filtered_news)} news articles. Interval: {start_date} - {end_date}")
        return self.convert_to_news_objects(filtered_news)

    def fetch_news(self, num_first: int, num_fin: int) -> list[dict]:
        """
        Helper method to fetch news from Anadolu Ajansı.

        :param num_first: The starting index for fetching news.
        :param num_fin: The number of news items to fetch.
        :return: List of news dictionaries.
        """
        url = self.base_url
        payload = {
            'numFirst': num_first,
            'numFin': num_fin
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }


        try:
            logging.debug(f"Fetching news from Anadolu Ajansı: {url}")
            logging.debug(f"Payload: {payload}")  
            response = requests.post(url, data=payload, headers=headers)
            logging.debug(f"Response: {response.text}") 
            response.raise_for_status()
            # Check if the response text is "Search"
            if response.text.strip() == "\"Search\"":
                logging.debug("Reached the end of the news list.")
                return []
            news_list = response.json()
            return news_list
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching news from Anadolu Ajansı: {e}")
            return []

    def convert_to_news_objects(self, news_list: list[dict]) -> list[News]:
        """
        Convert a list of news dictionaries to a list of News objects.

        :param news_list: List of news dictionaries.
        :return: List of News objects.
        """
        news_objects = []
        for news in news_list:
            try:
                title = news['Title']
                content = news['Summary']
                date_time = self.parse_dotnet_date(news['CreateDate'])
                news_url = f"{self.base_url}/{news['Route']}/{news['ID']}"

                news_object = News(
                    title=title,
                    content=content,
                    date_time=date_time,
                    source=self.source,
                    news_url=news_url
                )
                news_objects.append(news_object)
            except Exception as e:
                logging.error(f"Error converting news to News object: {e}")
        return news_objects
    
    def parse_dotnet_date(self,date_str):
        # Extract the milliseconds part from the date string
        milliseconds = int(date_str[6:-2])
        # Convert milliseconds to seconds
        seconds = milliseconds / 1000
        # Create a datetime object from the Unix epoch
        date = datetime(1970, 1, 1) + timedelta(seconds=seconds)
        return date
