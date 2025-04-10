import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from common.new_class import News
from common.database.types.json_news_database import JSONNewsDatabase
import os
import json
#run this in the main project folder
class NewsScraper:
    def __init__(self, base_url, start_date, end_date,topic, date_format='%d/%m/%Y'):
        self.base_url = base_url
        self.start_date = start_date
        self.end_date = end_date
        self.topic = topic
        self.date_format = date_format
    
    def generate_urls(self):
        """
        Generate a list of URLs for the given date range
        """
        start = datetime.strptime(self.start_date, self.date_format)
        end = datetime.strptime(self.end_date, self.date_format)
        topic = self.topic
        delta = timedelta(days=1)
        
        urls = []
        current_date = start
        while current_date <= end:
            url = self.base_url.format(current_date.day, current_date.month, current_date.year,topic)
            urls.append(url)
            current_date += delta
        return urls
    
    def fetch_html(self, url):
        """
        Fetch the HTML content of a URL
        """
        try: 
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch URL {url}: {e}")
            return None
    
    def parse_html(self, html_content):
        """
        Parse the HTML content using BeautifulSoup
        """
        return BeautifulSoup(html_content, 'html.parser')

    def extract_news_data(self,soup):
        """
        Extract news data from a BeautifulSoup object
        """
        news_data = []
        news_cards = soup.find_all('div', class_='card card-type-horizontal')
        
        for card in news_cards:
            title_tag = card.find('h3')
            content_tag = card.find('p')
            date_tag = card.find('div', class_='text-gray smaller font-weight-normal')
            url_tag = card.find('a', href=True)
            if not all([title_tag, content_tag, date_tag, url_tag]):
                return None
                    
            title = title_tag.get_text(strip=True)
            content = content_tag.get_text(strip=True)
            date = date_tag.get_text(strip=True).replace('Yayın Tarihi: ', '')
            news_url = url_tag['href']
            
            news_data.append({
                'title': title,
                'content': content,
                'date': date,
                'news_url': news_url
            })
        return news_data
    
    def scrape_news_data(self):
        """
        Main method to scrape news data for the date range
        """
        urls = self.generate_urls()
        all_news_data = []
        all_news_url = set()
        for url in urls:
            logging.info(f"Scraping data from {url}")
            html_content = self.fetch_html(url)
            if html_content:
                soup = self.parse_html(html_content)
                news_data = self.extract_news_data(soup)
                
                # Filter out duplicate news articles
                filtered_news_data = []
                for news in news_data:
                    if news['news_url'] not in all_news_url:
                        all_news_url.add(news['news_url'])
                        filtered_news_data.append(news)
                all_news_data.extend(filtered_news_data)
            logging.info(f"Found {len(news_data)} news articles.")
        return all_news_data
    
def convert_to_news_objects(news_data_list, source):
    """
    Converts a list of news data dictionaries into a list of News objects.
    Args:
        news_data_list (list): A list of dictionaries, where each dictionary contains
                               news data with keys 'title', 'content', 'date', and 'news_url'.
        source (str): The source of the news data.
    Returns:
        tuple: A tuple containing two elements:
            - news_objects (list): A list of successfully created News objects.
            - failed_news (list): A list of dictionaries that failed to convert to News objects.
    Raises:
        Exception: If there is an error during the conversion of news data to News objects,
                   the error is logged and the news data is added to the failed_news list.
    """
    news_objects = []
    failed_news = []

    for news_data in news_data_list:
        try:
            #date_time = parser.parse(news_data['date'])
            date_time = datetime.strptime(news_data['date'], '%Y-%m-%d %H:%M:%S')
            news_object = News(
                title=news_data['title'],
                content=news_data['content'],
                date_time=date_time,
                source=source,
                news_url=news_data['news_url']
            )
            news_objects.append(news_object)
        except Exception as e:
            logging.error(f"Failed to convert news data to News object: {e}")
            failed_news.append(news_data)
            
    return news_objects, failed_news

def save_news_to_json(news_list, db_file):
    """
    Save a list of News objects to a JSON database file.
    
    Parameters:
    news_list (list): A list of News objects.
    db_file (str): The name of the JSON database file.
    """
    # Load existing data from the database file if it exists
    if os.path.exists(db_file):
        with open(db_file, 'r') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Convert existing data to News objects
    existing_news = [News.from_dict(news) for news in existing_data]

    # Create a set of existing news URLs for quick lookup
    existing_urls = {news.news_url for news in existing_news}

    # Filter out news that are already in the database
    new_news = [news for news in news_list if news.news_url not in existing_urls]

    # Append new news to the existing data
    existing_data.extend([news.to_dict() for news in new_news])

    # Save the updated data back to the database file
    with open(db_file, 'w') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)
    
    return existing_data

class Config:
    DB_FILE = "mynet_news_ekonomi.json"  # Use a SQLite database instead of JSON
    NEWS_SOURCE = "MYNET"
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set up logging
    # Create a JSON database
    database = JSONNewsDatabase(Config.DB_FILE)
    
    base_url = "https://finans.mynet.com/haber/arsiv/{}/{}/{}/{}/"
    start_date = "25/12/2024"
    end_date = "27/12/2024"
    #topic = "borsa"
    topic = "ekonomi"

    scraper = NewsScraper(base_url, start_date, end_date, topic)
    all_news = scraper.scrape_news_data()
    logging.info(f"Scraped {len(all_news)} news articles.")
    logging.info(f"Scraped news size = {len(all_news)}")
    
    logging.info("Converting news data to News objects...")
    news_objects, failed_news = convert_to_news_objects(all_news, source = Config.NEWS_SOURCE)
    logging.info(f"Converted {len(news_objects)} news articles to News objects.")
    logging.info(f"Failed to convert {len(failed_news)} news articles.")
    # all_database_news = save_news_to_json(news_objects, Config.DB_FILE)
    all_database_news = database.save_news(news_objects)
    logging.info(f"Saved {len(all_database_news)} news articles to the database.")
    