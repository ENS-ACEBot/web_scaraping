import requests
import logging
from datetime import datetime,timedelta
from common.new_class import News
from scrapers.abstract_news_scraper import AbstractNewsScraper
import urllib.parse

class AnadoluAjansiScraper(AbstractNewsScraper):
    """
    A scraper for fetching and processing news from Anadolu Ajansı.
    There is no historical data available, so the scraper can only fetch news for the current date or maybe 1 day before.
    """

    def __init__(self):
        """
        Initialize the scraper with base URL and source name.
        """
        self.base_url = "https://www.aa.com.tr/"
        super().__init__("ANADOLU_AJANSI")  # self.source = "ANADOLU_AJANSI"


    def scrape_time_interval(self, start_date: str, end_date: str) -> list[News]:
        """
        Main method to scrape news data for the date range.
        date_format='%Y-%m-%d'
        """
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Headers you might want to use (mimicking the browser a bit)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Length": "193",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.aa.com.tr/",
            "Referer" : "https://www.aa.com.tr/tr/search/?s=ekonomi",
            "Cookie" : "_ga=GA1.1.1450609110.1739812425; newcookiepolicy=0.0.0; NSC_CFUB_TFBSDI=ffffffff09f27bce45525d5f4f58455e445a4a423660; __RequestVerificationToken=h-BLyUTzq5qmOl8yxwkxnbfHQZlte5-8NQNfOrY6oF3fEqG4Cf40kPfT4eMZSNIe5hkVJUHhpwitP-S0HgmgIOI3UInUy9NpDVhZFSFCw7c1; _ga_GQSWLNRWXH=GS1.1.1740169022.17.1.1740171898.60.0.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        # # Create a session object (this will manage cookies automatically)
        # session = requests.Session()

        # # Make the GET request to the homepage
        # response_home = session.get("https://www.aa.com.tr/tr/search/?s=ekonomi#!", headers=headers)

        # # Check if the request was successful
        # if response_home.status_code == 200:
        #     print("Homepage request successful.")
        # else:
        #     print(f"Homepage request failed with status code: {response_home.status_code}")
        #     exit(0)
        # cookies_dict = session.cookies.get_dict()
        # # Print the cookies
        # for key, value in cookies_dict.items():
        #     print(f"{key}: {value}")
        
        #request_verification_token = cookies_dict.get("__RequestVerificationToken")
        request_verification_token = "8x6Z2cTxgI3Ps3XtxdBltTV2eebfP_3Vx5mno_IxSp36lrDkMnlQIyrLakzVB14GnFB848c_XS9r3Dz0CtCneIETtO_ezV4J50h4d55xCWo1"
        
        if not request_verification_token:
            print("Request verification token not found.")
            exit(0)
                
        payload = {
            "PageSize" : 100,
            "Keywords" : "ekonomi",
            "CategoryId" : None,
            "TypeId" : 1,
            "Page" : 2,
            "__RequestVerificationToken" : request_verification_token
        }

        
        response = requests.post("https://www.aa.com.tr/tr/Search/Search",data=payload, headers=headers)
        print(response.text)
        return None

    def extract_verification_token_from_cookies(cookies_dict):
        """
        Extracts the __RequestVerificationToken value from a dictionary of cookies.

        Args:
            cookies_dict: A dictionary of cookies (e.g., from requests.cookies.get_dict()).

        Returns:
            The __RequestVerificationToken value if found, otherwise None.
        """
        return cookies_dict.get("__RequestVerificationToken")

    # def scrape_time_interval(self, start_date: str, end_date: str) -> list[News]:
    #     """
    #     Main method to scrape news data for the date range.
    #     date_format='%Y-%m-%d'
    #     """
    #     start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    #     end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    #     # fetch the news_link from the page for given interval
    #     filtered_news = []
    #     num_first = 1
    #     num_fin = 5

    #     while True:
    #         news_list = self.fetch_news(num_first, num_fin)
    #         logging.debug(f"[Anadolu Ajansı] Fetched {len(news_list)} news articles.")
    #         if not news_list:
    #             break
            
            
    #         for news in news_list:
    #             news_date = datetime.strptime(news['StartDate'], '%d.%m.%Y').date()
    #             logging.debug(f"[Anadolu Ajansı] News date: {news_date}")
    #             if start_date <= news_date <= end_date:
    #                 filtered_news.append(news)
    #             elif news_date < start_date:
    #                 break

    #         num_first += 5

    #     logging.debug(f"[Anadolu Ajansı] Found {len(filtered_news)} news articles. Interval: {start_date} - {end_date}")
    #     return self.convert_to_news_objects(filtered_news)

    # def fetch_news(self, num_first: int, num_fin: int) -> list[dict]:
    #     """
    #     Helper method to fetch news from Anadolu Ajansı.

    #     :param num_first: The starting index for fetching news.
    #     :param num_fin: The number of news items to fetch.
    #     :return: List of news dictionaries.
    #     """
    #     url = self.base_url
    #     payload = {
    #         'numFirst': num_first,
    #         'numFin': num_fin
    #     }
    #     headers = {
    #         'Content-Type': 'application/x-www-form-urlencoded',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    #     }


    #     try:
    #         logging.debug(f"Fetching news from Anadolu Ajansı: {url}")
    #         logging.debug(f"Payload: {payload}")  
    #         response = requests.post(url, data=payload, headers=headers)
    #         logging.debug(f"Response: {response.text}") 
    #         response.raise_for_status()
    #         # Check if the response text is "Search"
    #         if response.text.strip() == "\"Search\"":
    #             logging.debug("Reached the end of the news list.")
    #             return []
    #         news_list = response.json()
    #         return news_list
    #     except requests.exceptions.RequestException as e:
    #         logging.error(f"Error fetching news from Anadolu Ajansı: {e}")
    #         return []

    # def convert_to_news_objects(self, news_list: list[dict]) -> list[News]:
    #     """
    #     Convert a list of news dictionaries to a list of News objects.

    #     :param news_list: List of news dictionaries.
    #     :return: List of News objects.
    #     """
    #     news_objects = []
    #     for news in news_list:
    #         try:
    #             title = news['Title']
    #             content = news['Summary']
    #             date_time = self.parse_dotnet_date(news['CreateDate'])
    #             news_url = f"{self.base_url}/{news['Route']}/{news['ID']}"

    #             news_object = News(
    #                 title=title,
    #                 content=content,
    #                 date_time=date_time,
    #                 source=self.source,
    #                 news_url=news_url
    #             )
    #             news_objects.append(news_object)
    #         except Exception as e:
    #             logging.error(f"Error converting news to News object: {e}")
    #     return news_objects
    
    # def parse_dotnet_date(self,date_str):
    #     # Extract the milliseconds part from the date string
    #     milliseconds = int(date_str[6:-2])
    #     # Convert milliseconds to seconds
    #     seconds = milliseconds / 1000
    #     # Create a datetime object from the Unix epoch
    #     date = datetime(1970, 1, 1) + timedelta(seconds=seconds)
    #     return date
