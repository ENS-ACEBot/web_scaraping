import json
import sys
from new_class import News

def sort_news(file_name):
    with open(file_name, 'r') as file:
        news_list = json.load(file)

    news_objects = [News.from_dict(news) for news in news_list]
    sorted_news_objects = sorted(news_objects)

    sorted_news_list = [news.to_dict() for news in sorted_news_objects]
    sorted_file_name = f"sorted_{file_name}"

    with open(sorted_file_name, 'w') as sorted_file:
        json.dump(sorted_news_list, sorted_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python news_sorter.py <filename>")
        sys.exit(1)

    file_name = sys.argv[1]
    sort_news(file_name)