from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import logging
from kap.kap_news_class import KapNews
import json
import os
from scrapers.abstract_news_scraper import AbstractNewsScraper
import time
import html
import common.bist_50 as bist_50
from common.new_class import News


DISCLOSURE_INTERVAL_ENDPOINT = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"
# usage = post request 
# body : { toDate: "%Y-%m-%d", fromDate: "%Y-%m-%d" }
DISCLOSURE_BY_INDEX_ENDPOINT = "https://www.kap.org.tr/tr/Bildirim/"
# "https://www.kap.org.tr/tr/Bildirim/<index>"
class KapNewsScraper(AbstractNewsScraper):
    """
    Scraper for fetching KAP disclosures.
    """
    def __init__(self):
        self.disclosure_date_format = "%Y-%m-%d"    
        pass
    
    def scrape_time_interval(self, start_date: str, end_date: str) -> list[News]:
        """
        Scrape news for the given time interval and return a list of News objects.
        date format : "YYYY-MM-DD"
        """
        # try:
        #     logging.info(f"Scraping news for time interval started : ")
        #     logging.info(f"Scraping KAP disclosures from {start_date} to {end_date}")
        #     fetched_disclosures = self.get_all_kap_disclosures_for_given_range(start_date, end_date)
        #     logging.info(f"Scraping for news for time interval finished : {len(fetched_disclosures)} disclosures fetched")
        #     logging.info(f"Filtering and extracting content for BIST 50 companies for proper type disclosures")
        #     kapNews = self.filter_kap_news_and_extract_content(fetched_disclosures, bist_50.BIST_50_SYMBOLS)
        #     logging.info(f"Filtered and extracted content for BIST 50 companies : {len(kapNews)} disclosures")
        #     logging.info(f"Converting KapNews to News objects")
        #     news_list = self.convert_kapnews_to_news(kapNews)
        #     logging.info(f"Converted KapNews to News objects : {len(news_list)} news")
        #     return news_list
        # except Exception as e:
        #     logging.error(f"Error occured while scraping news for time interval started : {e}")
        #     return []
        logging.info(f"Scraping news for time interval started : ")
        logging.info(f"Scraping KAP disclosures from {start_date} to {end_date}")
        fetched_disclosures = self.get_all_kap_disclosures_for_given_range(start_date, end_date)
        logging.info(f"Scraping for news for time interval finished : {len(fetched_disclosures)} disclosures fetched")
        logging.info(f"Filtering and extracting content for BIST 50 companies for proper type disclosures")
        kapNews = self.filter_kap_news_and_extract_content(fetched_disclosures, bist_50.BIST_50_SYMBOLS)
        logging.info(f"Filtered and extracted content for BIST 50 companies : {len(kapNews)} disclosures")
        logging.info(f"Converting KapNews to News objects")
        news_list = self.convert_kapnews_to_news(kapNews)
        logging.info(f"Converted KapNews to News objects : {len(news_list)} news")
        return news_list
    
    def save_disclosures_json(self, kap_disclosures: list[KapNews], from_date: str, to_date: str, directory: str):
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
        file_path = f"{directory}/kap_disclosures_{from_date}_{to_date}.json"
        with open(file_path, 'w') as file:
            json.dump([disclosure.to_dict() for disclosure in kap_disclosures], file, ensure_ascii=False, indent=4)
        logging.info(f"KAP disclosures saved to {file_path}")
    
    # fetch all kap disclosures in the given range and return the list of KapNews objects without content
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
            
            logging.info(f"Fetched disclosures from {curr_start} to {curr_end} : total disclosure = {len(kap_disclosures)}\n")
            
            # sleep for 1 second to avoid rate limiting
            time.sleep(0.1)
            kap_disclosures = []
            curr_start = curr_end + timedelta(days=1)

            
        logging.info("-" * 50)
        logging.info(f"All discloures fetched from {from_date} to {to_date}")
        logging.info(f"Total {len(all_kap_disclosures)} disclosures fetched.")
        logging.info("-" * 50)  
        return all_kap_disclosures

    # fetch the kap disclosures from the given date range and return the list of KapNews objects without content
    def fetch_kap_disclosures(self, from_date: str, to_date: str) -> list[KapNews]:
        """
        Sends a POST request to the KAP API to retrieve disclosures within the given date range.
        
        Args:
            from_date (str): The start date in "YYYY-MM-DD" format.
            to_date (str): The end date in "YYYY-MM-DD" format.
        
        Returns:
            List[KapNews]: A list of KapNews objects.
        """
        url = DISCLOSURE_INTERVAL_ENDPOINT
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
   
    ###### main function to fetch disclosures without content in the given interval and save disclosures in the json files
    # it is used to fetch and save the disclosures in the given interval 
    def fetch_kap_disclosures_interval_year(self,start_year: int, end_year: int):
        '''
            divide kap disclosures into years and fetch them
        '''
        for i in range(start_year,end_year,-1):
            from_date   = f"{i}-01-01"
            to_date     = f"{i}-12-31" 
            kap_disclosures = self.get_all_kap_disclosures_for_given_range(from_date=from_date, to_date=to_date)
            self.save_disclosures_json(kap_disclosures, from_date, to_date, "kap/data")
    
    # it is used to retrive the kap disclosures from the json files
    def load_kap_news_from_json_files(self,directory: str) -> list[KapNews]:
        """
        Load KapNews objects from JSON files in the specified directory, starting from the given year and decreasing until the end year.

        Parameters:
        start_year (int): The starting year.
        end_year (int): The ending year.
        directory (str): The directory containing the JSON files.

        Returns:
        List[KapNews]: A list of KapNews objects.
        """
        kap_news_list = []

        file_path = directory
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for item in data:
                    kap_news_list.append(KapNews.from_dict(item))
        else:
            print(f"File not found: {file_path}")
            
        return kap_news_list
    
    # scrape the given indexed disclousre's content from the kap website and return the content
    # condition : disclosureClass = ODA, disclosureCategory = ODA
    def scrape_disclosure_by_index_ODA_ODA(self,index: int) -> str:
        """
        Scrape the disclosure details from the endpoint using the given index.

        Parameters:
        index (int): The index of the disclosure to scrape.

        Returns:
        dict: A dictionary containing the scraped disclosure details.
        """
        url = f"{DISCLOSURE_BY_INDEX_ENDPOINT}{index}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        max_retries = 9
        retry_delay = 2  # Initial delay in seconds
        logging.info(f"[ODA_ODA] Fetching disclosure by index {index}")
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an error for non-200 responses

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the div with the specified class
                content_div = soup.find('td', class_='taxonomy-context-value-summernote multi-language-content content-tr')
                if not content_div:
                    print(f"Content div not found for index {index}")
                    return {}

                # Extract the text inside the text-block-value div
                text_block = content_div.find('div', class_='text-block-value')
                if not text_block:
                    print(f"Text block not found for index {index}")
                    return {}
                content_text = text_block.get_text(separator=' ', strip=True)            # ensure the space between different blocks
                content_text = content_text.replace('\xa0', ' ')              # ensure the conversion of binary-space to normal space
                content_text = html.unescape(content_text)  # Unescape HTML entities ( " \' " -> " ' " )
                return content_text

            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed to fetch KAP disclosures: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        print(f"Failed to fetch disclosure by index {index}: {e}")
        return ""
    
    # scrape the given indexed disclousre's content from the kap website and return content
    # condition : disclosureCategory = STT, disclosureClass = ODA
    def scrape_disclosure_by_index_ODA_STT(self,index: int) -> str:
        """
        Scrape the disclosure details from the endpoint using the given index.

        Parameters:
        index (int): The index of the disclosure to scrape.

        Returns:
        dict: A dictionary containing the scraped disclosure details.
        """
        url = f"{DISCLOSURE_BY_INDEX_ENDPOINT}{index}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        max_retries = 9
        retry_delay = 2  # Initial delay in seconds
        logging.info(f"[ODA_STT] Fetching disclosure by index {index}")
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an error for non-200 responses

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the div with the specified class
                table_div = soup.find('div', class_='disclosureScrollableArea')
                if not table_div:
                    print(f"disclosureScrollableArea div not found for index {index}")
                    return {}

                # Extract the text inside the text-block-value div
                td_elements = table_div.find_all('td')
                if not td_elements:
                    print(f"Table elements not found for index {index}")
                    return {}
                
                # Get the text of the last td element
                last_td_text = td_elements[-1].get_text(strip=True)
                for i in range(1, len(td_elements)):
                    last_td_text = td_elements[-i].get_text(strip=True)
                    if last_td_text == "Ek Açıklamalar":
                        last_td_text = td_elements[-i+1].get_text(strip=True)
                        break
                
                if(last_td_text == ""):
                    print(f"Ek aciklama not found for index {index}")
                    return {}
                    
                last_td_text = last_td_text.replace('\xa0', ' ')  # Replace non-breaking spaces with regular spaces
                last_td_text = html.unescape(last_td_text)  # Unescape HTML entities
                return last_td_text

            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed to fetch KAP disclosures: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        print(f"Failed to fetch disclosure by index {index}: {e}")
        return ""
    
    def convert_kapnews_to_news(self,kap_news_list: list[KapNews]) -> list[News]:
        """
        Convert a list of KapNews objects to a list of News objects.

        Parameters:
        kap_news_list (List[KapNews]): A list of KapNews objects.

        Returns:
        List[News]: A list of News objects.
        """
        news_list = []
        for kap_news in kap_news_list:
            title = f"{kap_news.disclosure_index} - {kap_news.stock_codes} - {kap_news.kap_title}"
            news = News(
                title=title,
                content=kap_news.content,
                date_time=kap_news.publish_date,
                source="KAP", 
                news_url=f"https://www.kap.org.tr/tr/Bildirim/{kap_news.disclosure_index}" 
            )
            news_list.append(news)
        return news_list
    
    def filter_kap_news_and_extract_content(self,disclosures: list[KapNews], stock_codes: list[str]) -> list[KapNews]:
        '''
            filter the kap news list by stock codes and disclosure type and extract the content
        '''
        nw_disclosures = []
        cnt = 0
        print(len(disclosures))
        for disclosure in disclosures:
            if(disclosure.stock_codes in bist_50.BIST_50_SYMBOLS):
                print(f"found : {disclosure.stock_codes} - {disclosure.disclosure_index}")
                if disclosure.disclosure_class == "ODA" :
                    if disclosure.disclosure_category == "STT":
                        content = self.scrape_disclosure_by_index_ODA_STT(disclosure.disclosure_index)
                        if content == "": 
                            logging.info(f"Failed to fetch content for index {disclosure.disclosure_index}")
                            continue
                        disclosure.content = content
                        nw_disclosures.append(disclosure)
                        
                    elif disclosure.disclosure_category == "ODA" or disclosure.disclosure_type == "ODA":
                        content = self.scrape_disclosure_by_index_ODA_ODA(disclosure.disclosure_index)
                        if content == "": 
                            logging.info(f"Failed to fetch content for index {disclosure.disclosure_index}")
                            continue
                        disclosure.content = content
                        nw_disclosures.append(disclosure)
                    time.sleep(0.01)
            logging.info(f"Processed {cnt} disclosures : remaining {len(disclosures) - cnt}")
            cnt+=1
        return nw_disclosures
    
    def save_news_to_json(self,news_list, db_file):
        """
        Save a list of News objects to a JSON database file.
        
        Parameters:
        news_list (list): A list of News objects.
        db_file (str): The name of the JSON database file.
        """
        # Append new news to the existing data
        news_data = [news.to_dict() for news in news_list]

        # Save the updated data back to the database file
        with open(db_file, 'w') as file:
            json.dump(news_data, file, ensure_ascii=False, indent=4)
        
        return news_data
        
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     scraper = KapNewsScraper()
#     # 2017 den once old kap oluyormus orda farkli bir data scraping lazim
#     # get old scraped disclosures data
#     # for i in range(2017,2024):
#     #     cnt = 0
#     #     from_date   = f"{i}-01-01"
#     #     to_date     = f"{i}-12-31"         
#     #     disclosures = scraper.load_kap_news_from_json_files(i,i+1, "kap/data")
#     #     print(f"Loaded {len(disclosures)} disclosures - {from_date} to {to_date}")
#     #     nw_disclosures = scraper.filter_kap_news_and_extract_content(disclosures, bist_50.BIST_50_SYMBOLS)
#     #     scraper.save_disclosures_json(nw_disclosures, from_date, to_date, "kap/data_with_content_bist50")
#     #     print(f"Saved {len(nw_disclosures)} disclosures - {from_date} to {to_date} ")
#     for i in range(2017,2025):
#         cnt = 0
#         from_date   = f"{i}-01-01"
#         to_date     = f"{i}-12-31"    
#         file_name = f"kap/data_with_content_bist50/kap_disclosures_{from_date}_{to_date}.json"
#         disclosures =  scraper.load_kap_news_from_json_files(file_name)
#         news_list = scraper.convert_kapnews_to_news(disclosures)
#         print(f"Converted {len(news_list)} disclosures to news")
#         db_file = f"kap/data_with_content_bist50_general_class/news_{from_date}_{to_date}.json"
#         scraper.save_news_to_json(news_list,db_file)
#     # try to fetch single disclosure's aciklamalar ODA ODA
#     # index = 988819
#     # print(scraper.scrape_disclosure_by_index_ODA_ODA(index))
#     # logging.info("Done")
#     # index = 1388482
#     # disclosure_details = scraper.scrape_disclosure_by_index_ODA_ODA(index)
#     # print(disclosure_details["content"])  # Print the content directly

#     # try to fetch single disclosure's aciklamalar ODA STT
#     # index = 1365798
#     # disclosure_details = scraper.scrape_disclosure_by_index_ODA_STT(index)
#     # print(disclosure_details)  # Print the content directly
#     # print()
#     # index = 1365794
#     # disclosure_details = scraper.scrape_disclosure_by_index_ODA_STT(index)
#     # print(disclosure_details)  # Print the content directly
    