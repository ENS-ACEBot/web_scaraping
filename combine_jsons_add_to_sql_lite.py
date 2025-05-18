import os
import json
import sqlite3

DATABASE_PATH = 'ace_scraper/data/sql_news.db'

def create_database(db_path=DATABASE_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            date TEXT,
            source TEXT,
            news_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_news(news_list, db_path=DATABASE_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for news in news_list:
        title = news.get('title')
        content = news.get('content')
        date = news.get('date_time')
        source = news.get('source')
        news_url = news.get('news_url')

        # Convert dicts to JSON strings
        if isinstance(title, dict):
            title = json.dumps(title)
        if isinstance(content, dict):
            content = json.dumps(content)

        cursor.execute('''
            INSERT INTO news (title, content, date, source,news_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, date, source,news_url))
    conn.commit()
    conn.close()


def read_news_from_folder(folder_path):
    news_items = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        news_items.extend(data)
                    elif isinstance(data, dict):
                        news_items.append(data)
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
    return news_items

def read_news_from_file(file_path):
    if not os.path.isfile(file_path):
        print("File does not exist.")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                print("Unknown JSON structure.")
                return []
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []



def main():

    create_database()
    news_data = []
    # news_data = read_news_from_folder("/Users/burakersoz/Desktop/Sabanci_2024_Fall/ENS491/webscraping/old_scrapers/kap/data_with_content_bist50_general_class")
    # news_data += read_news_from_file("/Users/burakersoz/Desktop/Sabanci_2024_Fall/ENS491/webscraping/old_scrapers/mynet/data/mynet_news_combined.json")
    # news_data += read_news_from_file("/Users/burakersoz/Desktop/Sabanci_2024_Fall/ENS491/webscraping/old_scrapers/bigpara/bigpara_combined.json")
    news_data += read_news_from_file("/Users/burakersoz/Desktop/Sabanci_2024_Fall/ENS491/webscraping/old_scrapers/bloomberg/bloomberg_news.json")
    
    if news_data:
        insert_news(news_data)
        print(f"Inserted {len(news_data)} news articles into the database.")
    else:
        print("No valid news data found.")

if __name__ == "__main__":
    main()
