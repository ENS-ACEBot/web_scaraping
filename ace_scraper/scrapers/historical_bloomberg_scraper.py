from datetime import datetime
from typing import List, Tuple
import concurrent.futures as cf
import logging
import time
from typing import Iterable, List, Optional
from urllib.parse import quote,quote_plus
import bs4
import requests
from scrapers.abstract_news_scraper import AbstractNewsScraper
from common.new_class import News
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# i did not encounterd with rate limit :)
class Historical_Bloomberg_Scraper(AbstractNewsScraper):
    """
    Scrapes https://www.bloomberght.com/infinite/arama/<term>/p<page>
    concurrently for all BIST-30 symbols.
    """
    ARTICLE_THREADS = 20        # one per article (tweak if you hit rate limits)
    MAX_THREADS = 20          # one per symbol (tweak if you hit rate limits)

    def __init__(self):
        super().__init__(source="BloombergHT")

    # ---------- public interface ---------- #
    def scrape_time_interval(self,
                             start_date: str,    # “YYYY-mm-dd”  (not used now)
                             end_date: str       # “YYYY-mm-dd”
                             ) -> List[News]:
        """
        For every symbol → human name → search term, crawl all result pages
        until the endpoint signals ‘last page’.  Returns *deduplicated* `News`
        objects, sorted newest → oldest.
        """
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_news: set[News] = set()
        for sym in BIST30_NAME_MAP.keys():
            news_for_sym = self.crawl_symbol(sym,start_date, end_date)
            all_news.update(news_for_sym)
            
        # sort *descending* by date if available
        sorted_news = sorted(all_news,
                             key=lambda n: n.date_time or datetime.min,
                             reverse=True)
        return sorted_news

    # ---------- internals ---------- #
    def crawl_symbol(self, symbol: str, start_date :datetime, end_date:datetime) -> List[News]:
        human_name = BIST30_NAME_MAP[symbol]
        page = 1
        collected: List[News] = []
        collected_lock = Lock()
        end_of_time_flag = False
        last_page = 10000
        
        # ---------- 1) card pagination ---------- #
        # first fetch the news from paginated news pages, then fetch the dates
        while True:
            with ThreadPoolExecutor(max_workers=self.MAX_THREADS) as ex:
                fut_map = {ex.submit(fetch_one_page, human_name, page_i): page_i for page_i in range(page, page + self.MAX_THREADS)}
                
                for fut in as_completed(fut_map):
                    page_i = fut_map[fut]
                    html_text = fut.result()
                    if html_text is None:
                        last_page = min(last_page, page_i)
                        end_of_time_flag = True
                        continue
                    new_cards = parse_cards(html_text, source=self.source)
                    with collected_lock:
                        collected.extend(new_cards)
                logging.info(f"{page} - {page+ self.MAX_THREADS} for {symbol} news without date fetched")
            if end_of_time_flag:
                break
            logging.info(f"Fetching pages for {symbol} end, last page : {last_page}")
            page += self.MAX_THREADS
            
            
        print("collected:", len(collected))
            

        counter_lock = Lock()
        count = 0
        
        logging.info(f"For {symbol} Dates of the articles are fetching...")
        # for each news, fetch the date from the news page
        # ---------- 2) enrich with article dates ---------- #
        with ThreadPoolExecutor(max_workers=self.ARTICLE_THREADS) as ex:
            fut_map = {ex.submit(fetch_date_from_article, n.news_url): n
                    for n in collected}
            for fut in as_completed(fut_map):
                news_obj = fut_map[fut]
                date_val = fut.result()
                with counter_lock:
                    count += 1
                    if count % 10 == 0:
                        logging.info(f"For {symbol} is fetching... {count}/{len(collected)}")
                if date_val:
                    news_obj.date_time = date_val
                else:
                    #raise ValueError("Date not found for %s", news_obj.news_url)
                    logging.debug("Page {page} for {symbol} Date-fetch failed for %s", news_obj.news_url)
                    
    
        return collected

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BIST30Scraper/1.0; +https://github.com/you)",
}

# bloomberght_scraper.py
BIST30_NAME_MAP: dict[str, str] = {
    "AEFES": "Efes",
    "AKBNK": "Akbank",
    "ALARK": "Alarko",
    "ASELS": "Aselsan",
    "ASTOR": "Astor",
    "BIMAS": "Bim",
    "EKGYO": "Emlak Konut",#
    "ENKAI": "Enka",
    "EREGL": "Eregli",#
    "FROTO": "Ford",
    "GARAN": "Garanti", #
    "HEKTS": "Hektas", #
    "ISCTR": "Is Bankasi", ### turkish
    "KCHOL": "Koc Holding", #
    "KONTR": "Kontrolmatik",
    "KOZAL": "Koza Altin", #
    "KRDMD": "Kardemir",
    "MGROS": "Migros",
    "PETKM": "Petkim",
    "PGSUS": "Pegasus", #
    "SAHOL": "Sabanci", ## timeout
    "SASA": "Sasa",
    "SISE": "Sisecam", #
    "TCELL": "Turkcell", #
    "THYAO": "THY", #### timout
    "TOASO": "Tofas", #
    "TTKOM": "Telekom",
    "TUPRS": "Tupras", # timeout
    "ULKER": "Ulker", #
    "YKBNK": "Yapi Kredi", # turksih
}


def build_url(search_term: str, page: int) -> str:
    safe = quote_plus(search_term, safe="")
    # print("safe:", safe)    
    return f"https://www.bloomberght.com/infinite/arama/{safe}/p{page}"

def is_last_page(response: requests.Response) -> bool:
    """
    Returns True if the response is a valid 200 OK but has no useful data.
    """
    body = response.text.strip()
    if response.status_code == 200 and (body == "" or body == None):
        return True
    return False

def fetch_one_page(search_term: str, page: int, timeout: int = 10) -> Optional[str]:
    logging.info(f"fetching page: {page} - {search_term}")
    url = build_url(search_term, page)
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        if is_last_page(r):
            return None
        return r.text
    except requests.HTTPError as e:
        if r.status_code == 429:
            logging.warning("Rate-limited (429) on %s page %s", search_term, page)
        else:
            logging.error("HTTP error %s on %s page %s", e, search_term, page)
        return None
    except requests.RequestException as e:
        logging.error("Request failed: %s on %s page %s", e, search_term, page)
        return None

def parse_cards(html_text: str, source: str) -> List["News"]:
    soup = bs4.BeautifulSoup(html_text, "html.parser")
    cards = soup.select("div.tab-content > div[data-type^='news-card'] > a")
    news: List[News] = []
    for a in cards:
        title = a["title"].strip()
        url = "https://www.bloomberght.com" + a["href"]
        # BloombergHT does NOT expose the article date in the card;
        # you may fetch the article page in a future improvement.
        snippet = (a.select_one("figcaption div:nth-of-type(2)") or
                   a.select_one("figcaption div:nth-of-type(1)"))
        content_preview = snippet.get_text(" ", strip=True) if snippet else ""
        if title != "Piyasalarda gün sonu":
            news.append(News(title=title,
                            source=source,
                            news_url=url,
                            content=content_preview,
                            date_time=None))      # ← will be filled later if needed
    return news



# ---------- Turkish month name → integer ---------- #
_TR_MONTHS = {
    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
    "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12,
}

_DATE_RE = re.compile(
    r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4}).*?(\d{1,2}):(\d{2})"
)

def tr_date_to_dt(text: str) -> Optional[datetime]:
    """
    Converts '12 Mayıs 2025, Pazartesi 11:46' → datetime(2025, 5, 12, 11, 46)
    """
    m = _DATE_RE.search(text)
    if not m:
        return None
    day, month_tr, year, hour, minute = m.groups()
    month = _TR_MONTHS.get(month_tr)
    if not month:
        return None
    return datetime(int(year), month, int(day), int(hour), int(minute))

def fetch_date_from_article(url: str) -> Optional[datetime]:
    """
    Downloads the article page and extracts the date using the XPath you provided
    (/html/body/main/div[1]/div[2]/div[1]/article/div[1]/div[3]).
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        #print("html:", r.text)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        news_class = soup.find("div", class_="news-wrapper it-container relative flex flex-wrap")
        #print("news_class:", news_class)
        info_box = news_class.find("div", class_="flex items-center justify-between gap-2 w-full border-b-2 border-gray-500 mb-2 pb-2 w-1/2")
        #print("info_box:", info_box)
        info_div = info_box.find("div", class_="text-xs")
        #print("info_div:", info_div)
        if not info_div:
            return None
        date_text = info_div.get_text(" ", strip=True)
        return tr_date_to_dt(date_text)
    except Exception as exc:                         
        logging.debug("Date-fetch failed for %s: %s", url, exc)
        return None

