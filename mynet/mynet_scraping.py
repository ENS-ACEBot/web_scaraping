import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from new_class import News
import json
import os


def generate_urls(start_date, end_date):
    """
    Generate URLs for the given date interval.
    
    Parameters:
    start_date (str): The start date in the format 'dd/mm/yyyy'.
    end_date (str): The end date in the format 'dd/mm/yyyy'.
    
    Returns:
    list: A list of URLs.
    """
    base_url = "https://finans.mynet.com/haber/arsiv/{}/{}/{}/borsa/"
    start = datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.strptime(end_date, "%d/%m/%Y")
    delta = timedelta(days=1)
    
    urls = []
    current_date = start
    while current_date <= end:
        url = base_url.format(current_date.day, current_date.month, current_date.year)
        urls.append(url)
        
        current_date += delta
    return urls

def scrape_news_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    news_data = []
    news_cards = soup.find_all('div', class_='card card-type-horizontal')
    
    for card in news_cards:
        title_tag = card.find('h3')
        content_tag = card.find('p')
        date_tag = card.find('div', class_='text-gray smaller font-weight-normal')
        url_tag = card.find('a', href=True)
        
        if title_tag and content_tag and date_tag and url_tag:
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

def convert_to_news_objects(news_data_list, source):
    """
    Convert a list of news data dictionaries to a list of News objects.
    
    Parameters:
    news_data_list (list): A list of dictionaries containing news data.
    source (str): The source of the news.
    
    Returns:
    tuple: A tuple containing a list of News objects and a list of failed news dictionaries.
    """
    news_objects = []
    failed_news = []
    
    for news_data in news_data_list:
        try:
            #2024-01-23 13:29:38
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
            print(f"Failed to convert news data to News object: {e}")
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

def fetch_all_news_from_json(db_file):
    """
    Fetch all news data from the given JSON database file.
    
    Parameters:
    db_file (str): The name of the JSON database file.
    
    Returns:
    list: A list of News objects.
    """
    if os.path.exists(db_file):
        with open(db_file, 'r') as file:
            existing_data = json.load(file)
        news_objects = [News.from_dict(news) for news in existing_data]
        return news_objects
    else:
        return []


DB_FILE = "mynet_news.json"
NEWS_SOURCE = "MYNET"
# Example usage:
start_date = "25/12/2012"
end_date = "26/12/2024"
urls = generate_urls(start_date, end_date)
print("Urls to scrape:")
for url in urls:
    print(url)

print("-" * 80)
print("Scraped news data:")
print("-" * 80)
for url in urls:
    news_dictionary_data = scrape_news_data(url)
    news_class_data,failed_news = convert_to_news_objects(news_dictionary_data, "MYNET")
    print(f"Url : {url}")
    print(f"\033[92mTotal news: {len(news_class_data)}\033[0m")  # 92 is for green color
    print(f"\033[91mFailed news: {len(failed_news)}\033[0m")  # 91 is for red color
    print("-" * 80)
    # for news in news_class_data:
    #     print(f"Title: {news.title}")
    #     print(f"Content: {news.content}")
    #     print(f"Date: {news.date_time}")
    #     print(f"URL: {news.news_url}")
    #     print("-" * 80)
    save_news_to_json(news_class_data, DB_FILE)

all_news = fetch_all_news_from_json(DB_FILE)
print(f"All_news_size = : {len(all_news)}")