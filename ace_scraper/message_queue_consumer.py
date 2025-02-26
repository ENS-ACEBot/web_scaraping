from message_queue.RedisMessageQueue import RedisMessageQueueManager
from common.new_class import News
import json


CONFIG_FILE_PATH = "ace_scraper/env/config.json"

def read_config():
    '''
    This function reads the configuration file and returns the configuration as a dictionary.
    '''
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        config = {}
    return config

if __name__ == "__main__":
    
    redis = RedisMessageQueueManager()
    config = read_config()
    redis_queue_name = config.get("redis_news_message_queue", "news_queue")
    def callback(message):
        print("Received message: ")
        news = News.from_dict(message)
        print(f"Title: {news.title}")
        print(f"Date: {news.date_time}")
        print(f"Source: {news.source}")
        
    
    redis.listen_messages(callback)
    pass