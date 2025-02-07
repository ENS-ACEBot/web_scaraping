from scrapers.abstract_news_scraper import AbstractNewsScraper
from scrapers.mynet_scraper import MynetNewsScraper 
from scrapers.kap_scraper import KapNewsScraper
from scrapers.bigpara_scraper import BigparaNewsScraper
from database.types.sqllite_news_database import SQLLiteNewsDatabase
import logging
import datetime
from common.new_class import News
import schedule
import time
from logging.handlers import RotatingFileHandler

def scrape_and_save(database: SQLLiteNewsDatabase):
    try:
        # today's date
        fetching_date = datetime.datetime.now()
        date_format = '%Y-%m-%d'
        interval = datetime.timedelta(days=1)
        
        # preapre date to proper string format
        fetching_date_str = fetching_date.strftime(date_format)
        
        # add scrapers to list
        scrapers = [MynetNewsScraper(), KapNewsScraper(), BigparaNewsScraper()]

        all_news = []
        
        for scraper in scrapers:
            logging.info(f"Scraping data from {scraper.source} : interval {fetching_date_str}")
            
            scraper_news = scraper.scrape_time_interval(start_date=fetching_date_str, end_date=fetching_date_str)
            
            # get the last news for source and filter the news that are already in the database (earlier than the last news)
            last_news = database.get_query(source=scraper.source, limit=1)
            if last_news:
                last_news = last_news[0]
                logging.info(50*"-")
                logging.info(f"Last news in the database for {scraper.source} : {last_news.date_time}")
                logging.info(50*"-")
                # filter the news that are already in the database
                scraper_news = [news for news in scraper_news if news.date_time >= last_news.date_time]
            else :
                logging.info(f"No news found in the database for {scraper.source}")
            
            all_news.extend(scraper_news)
            
            logging.info(50*"-")
            logging.info(f"Scraped {len(scraper_news)} news from {scraper.source}")
            logging.info(50*"-")
            
            database.save_news(scraper_news)
            
        logging.info(50*"-")
        logging.info(f"Scraped total {len(all_news)} news articles.")
        logging.info(50*"-")
        
    except Exception as e:
        logging.error(f"An error occurred while scraping and saving news: {e}")
    

if __name__ == "__main__":
    
    database = SQLLiteNewsDatabase("data/sql_news.db")
    
    # set up logging
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    # log file
    log_file = "logs/news_scraper.log"
    
    # file handler
    # create new file for each 5MB and keep 2 backup files
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # set up logging
    logging.basicConfig(level=logging.INFO,handlers=[file_handler, console_handler])

    # run the function every 5 minutes, send parameter to the function
    schedule.every(20).seconds.do(scrape_and_save, database = database)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
        
    
    