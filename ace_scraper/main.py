from scrapers.abstract_news_scraper import AbstractNewsScraper
from scrapers.mynet_scraper import MynetNewsScraper 
from scrapers.kap_scraper import KapNewsScraper
from scrapers.bigpara_scraper import BigparaNewsScraper
from scrapers.anadolu_ajansi_scraper import AnadoluAjansiScraper
from database.sqllite_news_database import SQLLiteNewsDatabase
from message_queue.RedisMessageQueue import RedisMessageQueueManager
import os
import logging
import datetime
from common.new_class import News
import schedule
import time
from logging.handlers import RotatingFileHandler
import os
import json
import threading

total_saved_run = 0
CONFIG_FILE_PATH = "ace_scraper/env/config.json"

'''
TodoList:
- [ ] log the initialization of the redis message queue
- [ ] log the succesfull message sending
- [ ] fix the readme file
'''



def scrape_and_save_send_to_message_queue(scraper: AbstractNewsScraper,database: SQLLiteNewsDatabase, message_queue: RedisMessageQueueManager):
    '''
    This function scrapes news from the given scraper and saves them to the database.
    '''
    try:
        # today's date
        fetching_date = datetime.datetime.now()
        date_format = '%Y-%m-%d'
        interval = datetime.timedelta(days=1)
        
        # preapre date to proper string format
        fetching_date_str = fetching_date.strftime(date_format)
        
        logging.info(f"Scraping data from {scraper.source} : interval {fetching_date_str}")
        
        scraper_news = scraper.scrape_time_interval(start_date=fetching_date_str, end_date=fetching_date_str)
        
        # get the last news for source and filter the news that are already in the database (earlier than the last news)
        last_news = database.get_query(source=scraper.source, limit=1)
        if last_news:
            last_news = last_news[0]
            logging.info(f"Last news time in the database for {scraper.source} : {last_news.date_time}")
            # filter the news that are already in the database
            scraper_news = [news for news in scraper_news if news.date_time >= last_news.date_time and news.title != last_news.title]
        else :
            logging.info(f"No news found in the database for {scraper.source}")
        
        saved_news = database.save_news(scraper_news)
        
        saved_news_json = [news.to_dict() for news in saved_news]
        
        for news in saved_news_json:
            message_queue.send_message(news)
                                
        logging.info(f"Scraped total {len(scraper_news)} news articles from {scraper.source}. ")
        logging.info(f"Saved {len(saved_news)} news articles from {scraper.source}.")
        
        
    except Exception as e:
        logging.error(f"({scraper.source})An error occurred while scraping and saving news: {e}")

def read_config():
    '''
    This function reads the configuration file and returns the configuration as a dictionary.
    '''
    try:
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logging.error("Configuration file not found. Using default values.")
        config = {}
    return config


def run_scrapers_in_threads(scrapers, databases, message_queue):
    '''
    This function runs the scrapers in separate threads.
    '''
    logging.info("Running scrapers in separate threads.")
    
    threads = []
    for idx,scraper in enumerate(scrapers):
        thread = threading.Thread(target=scrape_and_save_send_to_message_queue, args=(scraper, databases[idx], message_queue))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    logging.info("Running scrapers in separate threads end.")
    
def setup_logging(log_file_path, file_log_level=logging.INFO, console_log_level=logging.INFO):
    '''
    This function sets up logging to a file.
    '''
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    # file handler
    # create new file for each 5MB and keep 2 backup files
    file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(file_log_level)
    
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_log_level)
    
    # set up logging
    logging.basicConfig(level=logging.DEBUG,handlers=[file_handler, console_handler])
        
if __name__ == "__main__":
    
    # Read configuration file
    config = read_config()
    
    log_file_path = config.get("log_file_path", "news_scraper.log") # if there is not value for log_file_path, use the default value
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)  # Ensure logs/ folder exists
    
    db_file_path = config.get("db_file_path", "sql_news.db")      # if there is not value for db_file_path, use the default value
    os.makedirs(os.path.dirname(db_file_path), exist_ok=True)  # Ensure data/ folder exists
    
    pid_file_path = config.get("pid_file_path", "process.pid")
    os.makedirs(os.path.dirname(pid_file_path), exist_ok=True)  # Ensure pid/ folder exists


    # Save the PID to a file
    pid = str(os.getpid())
    with open(pid_file_path, "w") as f:
        f.write(pid)
    
    # period time 
    scrape_period_seconds = config.get("scrape_period_seconds", 10)
    
    setup_logging(log_file_path, file_log_level=logging.INFO, console_log_level=logging.INFO)
    
    logging.info("News scraper started.")
    logging.info(f"logfile = {log_file_path}")
    logging.info(f"dbfile = {db_file_path}")
    logging.info(f"scrape_period_seconds = {scrape_period_seconds}")
    
    # create database object
    databases = [SQLLiteNewsDatabase(db_file_path),SQLLiteNewsDatabase(db_file_path),SQLLiteNewsDatabase(db_file_path)] #,SQLLiteNewsDatabase(db_file_path)]
    
    # create redis message queue object
    message_queue = RedisMessageQueueManager()
    
    # create scraper objects
    scrapers = [MynetNewsScraper(), KapNewsScraper(), BigparaNewsScraper()] #, AnadoluAjansiScraper()]
    
    # function to update the schedule (period time)
    def update_schedule():
        config = read_config()
        new_period_time_seconds = config.get("scrape_period_seconds", 10)
        if new_period_time_seconds != scrape_period_seconds:
            logging.info(f"Updating schedule period time to {new_period_time_seconds} seconds.")
            schedule.clear()
            schedule.every(new_period_time_seconds).seconds.do(run_scrapers_in_threads,scrapers=scrapers, databases=databases, message_queue = message_queue)
            return new_period_time_seconds
        return scrape_period_seconds
    
    # run the function every 5 minutes, send parameter to the function (initial schedule)
    schedule.every(scrape_period_seconds).seconds.do(run_scrapers_in_threads,scrapers = scrapers, databases = databases,message_queue = message_queue)
    
    while True:
        schedule.run_pending()
        scrape_period_seconds = update_schedule()
        time.sleep(1)
        
    
    