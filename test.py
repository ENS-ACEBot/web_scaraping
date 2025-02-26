from scrapers.anadolu_ajansi_scraper import AnadoluAjansiScraper
import logging



if __name__ == "__main__":
    scraper = AnadoluAjansiScraper()
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Scraping Anadolu Ajansi news for 2021-02-20")
    news = scraper.scrape_time_interval("2025-02-20", "2025-02-20")
    
    # logging.info(f"Found {len(news)} news articles.")
    # for n in news:
    #     logging.info(f"{n.date_time} - {n.title} - {n.news_url}")
    
    print("Hello World")