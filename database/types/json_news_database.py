import json
import os
from common.new_class import News

class JSONNewsDatabase:
    """
    A database handler class for storing and retrieving news articles in a JSON file.
    """
    def __init__(self, file_path="default_news.json"):
        """
        Initialize the JSONNewsDatabase instance.

        Parameters:
        file_path (str): The path to the JSON database file, specific to this instance.
        """
        self.file_path = file_path 
        self._ensure_file_exists()

        print(f"JSONNewsDatabase instance initialized with file: {self.file_path}")

    def _ensure_file_exists(self):
        """Ensure that the JSON file exists; create it if it doesn't."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump([], file)

    def save_news(self, news_list):
        """
        Save a list of News objects to the JSON database file.

        Parameters:
        news_list (list): A list of News objects to be saved.
        """
        updated_data = save_news_to_json(news_list, self.file_path)
        print(f"News saved to {self.file_path}. Total news count: {len(updated_data)}")
        return updated_data

    def get_all(self):
        """
        Retrieve all news articles from the JSON database.

        Returns:
        list: A list of News objects stored in the database.
        """
        with open(self.file_path, 'r') as file:
            news_list = json.load(file)
        return [News.from_dict(news) for news in news_list]

# Utility function for saving news
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
