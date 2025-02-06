from scrapers.abstract_news_scraper import AbstractNewsScraper
from scrapers.mynet_scraper import MynetNewsScraper 
from scrapers.kap_scraper import KapNewsScraper
from scrapers.bigpara_scraper import BigparaNewsScraper
from database.types.sqllite_news_database import SQLLiteNewsDatabase
import logging
import datetime
from common.new_class import News

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # today's date
    fetching_date = datetime.datetime.now()
    date_format = '%Y-%m-%d'
    interval = datetime.timedelta(days=1)
    
    fetching_date_str = fetching_date.strftime(date_format)
    scrapers = [MynetNewsScraper(), KapNewsScraper(), BigparaNewsScraper()]

    all_news = []

    database = SQLLiteNewsDatabase("data/sql_news.db")
    
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
    
    