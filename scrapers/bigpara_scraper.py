import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from common.new_class import News  # Assumes News has static method date_time_to_dateTime, to_dict(), and from_dict()
from scrapers.abstract_news_scraper import AbstractNewsScraper
import time
import threading


class BigparaNewsScraper(AbstractNewsScraper):
    """
    A scraper for fetching and processing news from Bigpara.
    """

    def __init__(self):
        """
        Initialize the scraper with base URL, news page URL, source name, and page count.

        :param base_url: The base URL of the Bigpara website.
        :param news_page_url: The URL prefix for paginated news listings.
        :param source: The name of the news source.
        :param page_count: Number of news listing pages to fetch.
        """
        self.base_url = "https://bigpara.hurriyet.com.tr"
        self.news_page_url = "https://bigpara.hurriyet.com.tr/haberler/tumu/bu-yil/"
        self.page_count = self.get_maximum_page_count()
        super().__init__("BIGPARA") # self.source = "BIGPARA"
        
    def scrape_time_interval(self, start_date: str, end_date: str) -> list[News]:
        '''
        date format = '%Y-%m-%d'
        '''
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # fetch the news_link from the page for given interval
        filtered_news = []
        for i in range(1, self.page_count + 1):
            news_list = self.fetch_links_from_page(self.news_page_url, i)
            flag = False
            for news in news_list:
                news_date = news.date_time.date()  # Extract the date part of news.date_time
                if start_date <= news_date <= end_date:
                    flag = True
                    filtered_news.append(news)
            if flag == False: # if the news is not in the interval break the loop
                break
        logging.debug(f"[Bigpara] Found {len(filtered_news)} news articles. Interval : {start_date} - {end_date}")
        # update all news content
        filtered_news = self.update_news_content(filtered_news)
        return filtered_news
        pass
    
    # get the maximum page count at bigpara website at all news 
    def get_maximum_page_count(self) -> int:
        """
        Get the maximum number of pages to scrape.

        :return: The maximum number of pages to scrape.
        """
        url = "https://bigpara.hurriyet.com.tr/haberler/tumu/bu-yil/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        pages_cover_element = soup.find("div",class_="sortOfBar pager")
        pages_elements = pages_cover_element.find_all("li", class_= "wide")
        # Extract the href attribute of the last page element
        last_page_element = pages_elements[-1].find("a")
        if last_page_element:
            href = last_page_element.get("href")
            # Extract the page number from the href
            maximum_page = int(href.split('/')[-2])
        else:
            maximum_page = 1  # Default to 1 if no pages found
        return maximum_page

    def fetch_links_from_page(self, url: str, page_number: int) -> list[News]:
        """
        Helper method to fetch news links from a single page.

        :param session: The aiohttp ClientSession object.
        :param page_number: The page number to fetch.
        :return: List of News objects from the page.
        """
        url = f"{url}{page_number}/"
        news_list = []
        max_retries = 8
        retry_delay = 0.5
        
        for attempt in range(1, max_retries + 1):
            try:
                # Fetch the page content
                response = requests.get(url)
                # Raise an exception for bad status codes
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')                    
                # Locate the news table – adjust the class selectors as needed.
                news_tables = soup.find_all(class_="tBody")
                if not news_tables:
                    raise ValueError("News table not found on page")
                
                # Each news listing is contained in a <ul> within the table
                news_items = news_tables[0].find_all("ul")
                logging.debug(f"Page {page_number}: Found {len(news_items)} news items.")

                for item in news_items:
                    # Extract title (assumes title is inside an h2 tag)
                    title_tag = item.find("h2")
                    if not title_tag:
                        continue
                    title = title_tag.text.strip()

                    # Extract the news URL – assume there is an anchor tag (<a>)
                    a_tag = item.find("a")
                    if not a_tag or "href" not in a_tag.attrs:
                        continue
                    news_url = self.base_url + a_tag["href"]

                    # Extract date and time (adjust class names according to the actual HTML)
                    date_li = item.find("li", class_="cell005")
                    time_li = item.find("li", class_="cell064")
                    if not date_li or not time_li:
                        continue
                    date_str = date_li.text.strip()
                    time_str = time_li.text.strip()

                    # Convert date and time using News’ helper (expects a static method)
                    date_time = News.date_time_to_dateTime(date_str, time_str)

                    news_item = News(
                        title=title,
                        source=self.source,
                        news_url=news_url,
                        date_time=date_time
                    )
                    news_list.append(news_item)
                break  # Exit retry loop on success

            except Exception as e:
                logging.error(f"Error fetching page {page_number} (attempt {attempt}/{max_retries}): {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        return news_list

    def update_news_content(self, news_list: list[News]) -> list[News]:
        """
        Update each News object with its full content by fetching its news URL.

        :param news_list: List of News objects (with links already fetched).
        :return: The same list of News objects with their content property updated.
        """
        logging.debug("Starting to update news content for each news item.")
        updated_count = 0
        disrupted_count = 0
        total = len(news_list)

        def fetch_and_update(news: News, index: int):
            nonlocal updated_count, disrupted_count
            
            max_retries = 8
            retry_delay = 0.5
            
            for attempt in range(1, max_retries + 1):
                try:
                    response = requests.get(news.news_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                                    
                    # news' header information
                    header_element = soup.find(class_="news-content__inf").find("h2").text
                    text = header_element + " "
                    
                    #check if it has news-content readingTime class if it has get the text
                    content_element = soup.find(class_="news-content readingTime")
                    if(content_element != None):
                        text_elements = content_element.find_all("p")
                        for t in text_elements:
                            text += t.text + " "
                    
                    #check if it has gallerylist class if it has get the text
                    content_element = soup.find(class_="gallery-list")
                    if(content_element != None):
                        text_elements = content_element.find_all("p")
                        for t in text_elements:
                            # sometimes the same text is duplicated because of the structure of the html, to prevent it check if it is the duplicated text
                            if(t.find("p") != None): 
                                continue
                            #print("text: ", t)
                            text += t.text + " "
                    # print("Content: \n",text,sep="")
                    # print("\n")
                    news_list[index].content = text
                    break  # Exit retry loop on success
                except requests.exceptions.RequestException as e:
                    logging.error(f"[Request exception] Error fetching content for news index {index} URL {news.news_url}: {e}")
                except Exception as ex:
                    disrupted_count += 1
                    logging.error(f"Error fetching content for news index {index} URL {news.news_url}: {ex}")
                    break
                
        thread_count = 0
        threads = []
        for idx, news in enumerate(news_list):
            logging.debug(f"Fetching content for news {idx + 1}/{total}: {news.title}")
            #fetch_and_update(news, idx)
            
            thread = threading.Thread(target=fetch_and_update, args=(news, idx))
            threads.append(thread)
            thread.start()
            thread_count += 1
            
            if(thread_count == len(news_list) - 1 or thread_count == 30):
                for t in threads:
                    t.join()
                thread_count = 0
                threads = []
                break

        # remove the news without content 
        news_list = [news for news in news_list if news.content]
        logging.debug(f"Finished updating news content. Updated: {len(news_list)}, Failed: {disrupted_count}")
        return news_list

    def save_news_to_json(self, news_list: list[News], json_file_name: str = "all_news.json") -> None:
        """
        Save a list of News objects to a JSON file.

        :param news_list: List of News objects.
        :param json_file_name: Destination JSON file name.
        """
        news_dict_list = [news.to_dict() for news in news_list]
        with open(json_file_name, 'w', encoding='utf-8') as outfile:
            json.dump(news_dict_list, outfile, ensure_ascii=False, indent=4)
        logging.debug(f"Saved {len(news_list)} news items to {json_file_name}.")

    def read_news_from_json(self, json_file_name: str = "all_news.json") -> list[News]:
        """
        Read News objects from a JSON file.

        :param json_file_name: The JSON file to read from.
        :return: List of News objects.
        """
        with open(json_file_name, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        news_list = [News.from_dict(item) for item in data]
        logging.debug(f"Loaded {len(news_list)} news items from {json_file_name}.")
        return news_list
