from datetime import datetime, timedelta
import requests
import logging
from kap.kap_news_class import KapNews
import json
import os
from scrapers.abstract_news_scraper import AbstractNewsScraper
import time



class KapNewsScraper(AbstractNewsScraper):
    """
    Scraper for fetching KAP disclosures.
    """
    disclosure_date_format = "%Y-%m-%d"
    
    def scrape_time_interval(self, start_date: str, end_date: str):
        """
        Scrapes KAP disclosures within the given date range.
        """
        # start = datetime.strptime(start_date, self.disclosure_date_format)
        # end = datetime.strptime(end_date, self.disclosure_date_format)

        # # Generate API query parameters (assuming KAP API supports filtering by date)
        # url = self.base_url.format(start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"))
        # logging.info(f"Fetching data from {url}")

        # json_data = self.fetch_json(url)
        # if not json_data:
        #     return []

        # return self.extract_news_data(json_data)
    
    def save_disclosures_json(self, kap_disclosures: list[KapNews], from_date: str, to_date: str):
        """
        Save the KAP disclosures to a JSON file. The file is saved in the 'kap/data' folder with the name 
        'kap_disclosures_<start-date>_<end-date>.json'. If the file does not exist, it will be created.

        Parameters:
        kap_disclosures (List[KapNews]): A list of KapNews objects containing the disclosure data.
        from_date (str): The start date in "YYYY-MM-DD" format.
        to_date (str): The end date in "YYYY-MM-DD" format.

        The function will:
        1. Convert the list of KapNews objects to dictionaries using their `to_dict` method.
        2. Save the JSON data to the specified file path.
        3. Log an info message indicating the file path where the disclosures were saved.

        save_disclosures_json(kap_disclosures, "2024-01-23", "2024-01-24")
        """
        file_path = f"kap/data/kap_disclosures_{from_date}_{to_date}.json"
        with open(file_path, 'w') as file:
            json.dump([disclosure.to_dict() for disclosure in kap_disclosures], file, ensure_ascii=False, indent=4)
        logging.info(f"KAP disclosures saved to {file_path}")
    
    def get_all_kap_disclosures_for_given_range(self, from_date: str, to_date: str):
        """_summary_
            it uses fetch_kap_disclosures method to get all kap disclosures with intervals
            interval is 1 months
        """
        start = datetime.strptime(from_date, self.disclosure_date_format)
        end = datetime.strptime(to_date, self.disclosure_date_format)
        delta = timedelta(days=3)
        all_kap_disclosures = []
        curr_start = start
        
        logging.info("-" * 50)
        logging.info(f"Fetching KAP disclosures from {from_date} to {to_date}")
        logging.info("-" * 50)
        
        while curr_start <= end:
            curr_end = curr_start + delta
            if curr_end > end:
                curr_end = end
                
            logging.info(f"Fetching disclosures from {curr_start} to {curr_end}")
            
            kap_disclosures = self.fetch_kap_disclosures(curr_start.strftime(self.disclosure_date_format), curr_end.strftime(self.disclosure_date_format))
            all_kap_disclosures.extend(kap_disclosures)
            
            logging.info(f"Fetched disclosures from {curr_start} to {curr_end} : {len(kap_disclosures)}\n")
            
            # sleep for 1 second to avoid rate limiting
            time.sleep(3)
            kap_disclosures = []
            curr_start = curr_end + timedelta(days=1)

            
        logging.info("-" * 50)
        logging.info(f"All discloures fetched from {from_date} to {to_date}")
        logging.info(f"Total {len(all_kap_disclosures)} disclosures fetched.")
        logging.info("-" * 50)  
        return all_kap_disclosures


    def fetch_kap_disclosures(self, from_date: str, to_date: str) -> list[KapNews]:
        """
        Sends a POST request to the KAP API to retrieve disclosures within the given date range.
        
        Args:
            from_date (str): The start date in "YYYY-MM-DD" format.
            to_date (str): The end date in "YYYY-MM-DD" format.
        
        Returns:
            List[KapNews]: A list of KapNews objects.
        """
        url = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "fromDate": from_date,
            "toDate": to_date
        }
        
        max_retries = 9
        retry_delay = 2  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()  # Raise an error for non-200 responses
                disclosures = response.json()

                if not isinstance(disclosures, list):
                    logging.error("Unexpected API response format")
                    return []

                kap_news_list = [KapNews.from_dict(item) for item in disclosures]
                return kap_news_list

            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed to fetch KAP disclosures: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        logging.error("All attempts to fetch KAP disclosures failed.")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = KapNewsScraper()
    
    for i in range(2024,2010,-1):
        from_date   = f"{i}-01-01"
        to_date     = f"{i}-12-31" 
        kap_disclosures = scraper.get_all_kap_disclosures_for_given_range(from_date=from_date, to_date=to_date)
        scraper.save_disclosures_json(kap_disclosures, from_date, to_date)
    # from_date   = "2023-01-02"
    # to_date     = "2024-01-01" 
    # kap_disclosures = scraper.get_all_kap_disclosures_for_given_range(from_date=from_date, to_date=to_date)
    # scraper.save_disclosures_json(kap_disclosures, from_date, to_date)
    
