from scrapers.kap_scraper import KapNewsScraper
from database.sqllite_news_database import SQLLiteNewsDatabase
import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from scrapers.historical_bloomberg_scraper import Historical_Bloomberg_Scraper, fetch_date_from_article
from database.json_news_database import JSONNewsDatabase

# === Provide your file paths below ===
DB_FILE_PATH = "ace_scraper/data/sql2_news.db"
JSON_DB_FILE_PATH = "ace_scraper/data/bloomberg_news.json"
LOG_FILE_PATH = "ace_scraper/logs/bloomberg_scraper.log"

def setup_logging(log_file_path):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

def scrape_kap_news_2007_to_2010():
    setup_logging(LOG_FILE_PATH)

    os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
    db = SQLLiteNewsDatabase(DB_FILE_PATH)
    scraper = KapNewsScraper()

    start_date = datetime(2024, 12, 1)
    end_date = datetime(2024, 12, 31)
    current_date = start_date

    while current_date <= end_date:
        next_day = current_date + timedelta(days=1)
        try:
            date_str = current_date.strftime('%Y-%m-%d')
            logging.info(f"[KAP] Scraping {date_str}")

            news_list = scraper.scrape_time_interval(
                start_date=date_str,
                end_date=next_day.strftime('%Y-%m-%d')
            )

            saved_news = db.save_news(news_list)
            logging.info(f"[KAP] Done: Scraped {len(news_list)}, saved {len(saved_news)}")

        except Exception as e:
            logging.error(f"[KAP] Error on {current_date.date()}: {e}")

        current_date = next_day

def bloomberg_scraper():
    scraper = Historical_Bloomberg_Scraper()
    # Setup logging
    setup_logging(LOG_FILE_PATH)

    #Create database object
    db = JSONNewsDatabase(JSON_DB_FILE_PATH)

    # Create scraper object
    scraper = Historical_Bloomberg_Scraper()

    # Scrape news data
    start_date = datetime(2025, 5, 1)
    end_date = datetime(2025, 5, 13)
    news_data = scraper.scrape_time_interval(start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))

    # Save news data to database
    saved_news = db.save_news(news_data)
    logging.info(f"[BLOOMBERG] Done: Scraped {len(news_data)}, saved {len(saved_news)}")
    # print(f"[BLOOMBERG] Done: Scraped {len(news_data)}")
    # for new in news_data:
    #     print(new.to_dict())
    pass

# filter out news with None date_time and special news
# such as "gün sonu", "hangi", "ekonomi basınında bugün"
# and save to a new JSON database
def remove_news_with_none_dates_and_special_news():
    # Load existing news from original database
    db = JSONNewsDatabase(JSON_DB_FILE_PATH)
    CLEANED_DB_FILE_PATH = "ace_scraper/data/cleaned_bloomberg_news.json"
    all_news = db.get_all()

    logging.warning(f"Loaded {len(all_news)} news items from original DB")

    # Filter news that have a valid date_time
    valid_news = [
        news for news in all_news
        if news.date_time is not None and
        "gün sonu" not in news.title.lower() and
        "hangi" not in news.title.lower() and
        "ekonomi basınında bugün" not in news.title.lower()
    ]
    logging.warning(f"Filtered {len(valid_news)} news items with non-null date_time")

    # Save to a new JSON database using JSONNewsDatabase
    cleaned_db = JSONNewsDatabase(CLEANED_DB_FILE_PATH)
    cleaned_db.save_news(valid_news)

    logging.warning(f"Saved valid news items to new database: {CLEANED_DB_FILE_PATH}")
    

if __name__ == "__main__":
    remove_news_with_none_dates_and_special_news()
