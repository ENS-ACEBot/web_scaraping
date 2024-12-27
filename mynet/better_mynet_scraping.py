import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from new_class import News
import os
import json

class NewsScraper:
    def __init__(self, base_url, start_date, end_date, date_format='%d/%m/%Y'):
        self.base_url = base_url
        self.start_date = start_date
        self.end_date = end_date
        self.date_format = date_format
    
    def generate_urls(self):
        """
        Generate a list of URLs for the given date range
        """
        start = datetime.strptime(self.start_date, self.date_format)
        end = datetime.strptime(self.end_date, self.date_format)
        delta = timedelta(days=1)
        
        urls = []
        current_date = start
        while current_date <= end:
            url = self.base_url.format(current_date.day, current_date.month, current_date.year)
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
        for url in urls:
            logging.info(f"Scraping data from {url}")
            html_content = self.fetch_html(url)
            if html_content:
                soup = self.parse_html(html_content)
                news_data = self.extract_news_data(soup)
                all_news_data.extend(news_data)
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
    try:
        # Check if file exists and read existing data, if not, initialize an empty list
        if os.path.exists(db_file):
            with open(db_file, 'r') as file:
                existing_data = json.load(file)
            logging.info(f"Loaded existing data from {db_file}")
        else:
            existing_data = []
            logging.info(f"No existing data found. Starting with an empty list.")

        # Extract existing URLs for quick lookup to avoid duplicates
        existing_urls = {news['news_url'] for news in existing_data}

        # Filter out news that already exist in the database
        new_news = [news for news in news_list if news.news_url not in existing_urls]

        # Log how many new news items are found
        logging.info(f"Found {len(new_news)} new news to be added.")

        # If there are new news, append to the existing data and save
        if new_news:
            existing_data.extend(new_news)

            # Write the updated data to the file
            with open(db_file, 'w') as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
            logging.info(f"Saved {len(new_news)} new news items to {db_file}.")
        else:
            logging.info("No new news items to add.")
    
    except Exception as e:
        # Log any error that occurs during the process
        logging.error(f"An error occurred while saving news to {db_file}: {e}", exc_info=True)


class Config:
    DB_FILE = "mynet_news.json"  # Use a SQLite database instead of JSON
    NEWS_SOURCE = "MYNET"
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set up logging
    
    base_url = "https://finans.mynet.com/haber/arsiv/{}/{}/{}/borsa/"
    start_date = "01/01/2022"
    end_date = "5/01/2022"
    
    scraper = NewsScraper(base_url, start_date, end_date)
    all_news = scraper.scrape_news_data()
    logging.info(f"Scraped {len(all_news)} news articles.")
    logging.info(f"Scraped news size = {len(all_news)}")
    
    logging.info("Converting news data to News objects...")
    news_objects, failed_news = convert_to_news_objects(all_news, source="Mynet")
    logging.info(f"Converted {len(news_objects)} news articles to News objects.")
    logging.info(f"Failed to convert {len(failed_news)} news articles.")
    save_news_to_json(news_objects, Config.DB_FILE)
    