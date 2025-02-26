import json
import sys
from collections import defaultdict
from new_class import News

def find_duplicates(file_name):
    try:
        with open(file_name, 'r') as file:
            news_list = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return
    news_objects = [News.from_dict(news) for news in news_list]
    news_count = len(news_objects)

    url_count = defaultdict(int)
    for news in news_objects:
        url_count[news.news_url] += 1

    duplicates = sum(1 for count in url_count.values() if count > 1)

    print(f"\033[92mNumber of news: {news_count}\033[0m")  # Green text
    print(f"\033[93mNumber of duplicates: {duplicates}\033[0m")  # Yellow text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_duplicates.py <file_name>")
    else:
        find_duplicates(sys.argv[1])
