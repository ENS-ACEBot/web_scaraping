from scrapers.abstract_news_scraper import AbstractNewsScraper
from scrapers.mynet_scraper import MynetNewsScraper 
from scrapers.kap_scraper import KapNewsScraper
from scrapers.bigpara_scraper import BigparaNewsScraper
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

    mynet_scraper = MynetNewsScraper()
    mynet_news = mynet_scraper.scrape_time_interval(fetching_date_str,fetching_date_str)

    kap_scraper = KapNewsScraper()
    
    kap_news = kap_scraper.scrape_time_interval(fetching_date_str,fetching_date_str)
    
    bigpara_scraper = BigparaNewsScraper()
    
    bigpara_news =  bigpara_scraper.scrape_time_interval(fetching_date_str,fetching_date_str)
    
    # for news in bigpara_news:
    #     print(news.title)
    #     print(news.date_time)

    