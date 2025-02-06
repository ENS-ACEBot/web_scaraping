from database.types.sqllite_news_database import SQLLiteNewsDatabase 
from common.new_class import News
import os
from typing import List
import json


def read_news_from_json_files(directory: str) -> list[News]:
    """
    Read news from all JSON files in the specified directory.

    Parameters:
    directory (str): The directory containing the JSON files.

    Returns:
    List[News]: A list of News objects.
    """
    news_list = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for item in data:
                    news = News.from_dict(item)
                    news_list.append(news)

    return news_list



if __name__ == "__main__":
    database = SQLLiteNewsDatabase("data/sql_news.db")
    directory = "/Users/burakersoz/Desktop/Sabanci_2024_Fall/ENS491/webscraping/data/json_data"
    news_list = read_news_from_json_files(directory)
    database.save_news(news_list)
    # for idx,new in enumerate(news_list):
    #     database.save_news([new])
    #     print(f"Saved {idx+1}/{len(news_list)} news to the database.")
    #     print(f"title : {new.news_url}")
    database_news = database.get_all()
    print(f"Read {len(news_list)} news articles from JSON files.")
    # for new in news_list[:1]:
    #     print(f"title : {new.title}")
    #     print(f"content : {new.content}")
    #     print(f"date_time : {new.date_time}")
    #     print(f"source : {new.source}")
    #     print(f"news_url : {new.news_url}")
    print(f"Read {len(database_news)} news articles from the database.")
    # for new in database_news:
    #     print(f"title : {new.title}")
    #     print(f"content : {new.content}")
    #     print(f"date_time : {new.date_time}")
    #     print(f"source : {new.source}")
    #     print(f"news_url : {new.news_url}")
    # kap_news = database.get_query( source="KAP")
    
    # compare all the elements
    # for i in range(len(news_list)):
    #     if(news_list[i] not in database_news):
    #         print(f"Not found in database {news_list[i].title}")
    # print("Finished comparing all elements")