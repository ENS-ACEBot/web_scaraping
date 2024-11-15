from urllib.request import urlopen, Request
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from new_class import News
import json
import chardet



def print_indent(string, indent_count=1):
    indent_string = "----"
    print(indent_string*indent_count, string)

def get_news_links(base_url,news_page_url,SOURCE,page_count=1):
    all_news = []
    # 40 pages
    print_indent("Getting news links from bigpara")
    for i in range(page_count):
        url = news_page_url + str(i+1) + "/"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        newsTable = soup.find_all(class_="tBody")
        newslist = newsTable[0].find_all("ul")
        print("Page: ", i+1, " News Count: ", len(newslist))
        for new in newslist:
            # find the title in news html which has tag with h2
            new_title = new.find("h2").text
            new_url = base_url + new.find("a")["href"]
            # date is kept in this html element : <li class="cell012 tar fsn">23.10.2024</li>
            date = new.find("li", class_="cell012 tar fsn").text
            time = new.find("li", class_="cell024 tar fsn").text
            date_time = News.date_time_to_dateTime(date, time)
            
            news_class = News( title= new_title, source=SOURCE, news_url=new_url,date_time=date_time) 
            all_news.append(news_class)
    print_indent("News links are fetched")

    print_indent(f"Total news count: {len(all_news)}")
    return all_news


async def update_news_with_content_async(all_news):
    # create lock for updating updated_news_count
    lock = asyncio.Lock()
    news_len = len(all_news)
    updated_news_count = 0
    # Asynchronous function to fetch and parse a single news URL
    async def fetch_news_content(session, news, index, news_url):
        # Declare updated_news_count as nonlocal to modify the variable in the outer scope, if you do not do that it cannot reach the outer scope
        nonlocal updated_news_count  
        url = news_url

        # Fetch HTML asynchronously
        try:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                # it is important to detect the encoding of the page because some pages may have different encoding than utf-8
                raw_content = await response.read()
                # decoe the raw content without errors
                html = raw_content.decode('utf-8', errors='ignore')
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # news' header information
                header_element = soup.find(class_="news-content__inf").find("h2").text
                text = header_element + " "
                
                #check if it has news-content readingTime class if it has get the text
                content_element = soup.find(class_="news-content readingTime")
                if(content_element != None):
                    text_elements = content_element.find_all("p")
                    for t in text_elements:
                        text += t.text + " "
                #check if it has gallerylist class if it has get the text
                content_element = soup.find(class_="gallery-list")
                if(content_element != None):
                    text_elements = content_element.find_all("p")
                    for t in text_elements:
                        # sometimes the same text is duplicated because of the structure of the html, to prevent it check if it is the duplicated text
                        if(t.find("p") != None): 
                            continue
                        #print("text: ", t)
                        text += t.text + " "
                # print("Content: \n",text,sep="")
                # print("\n")
                all_news[index].content = text
            async with lock:
                updated_news_count += 1
                print(f"Content fetched: {updated_news_count}/{news_len}")
                    

        except Exception as e:
            print("Error:", e)
            print("index:", index)
            print("Error in news:", news.news_url)
            print("\n")

    async def fetch_all_news_async():
        async with aiohttp.ClientSession() as session:
            tasks = [
                fetch_news_content(session, news, index, news_url=news.news_url)
                for index, news in enumerate(all_news)
            ]
            await asyncio.gather(*tasks)
    print_indent("Fetching news content...")
    await fetch_all_news_async()
    print_indent("News content fetched.")
    
    return all_news

def save_news_to_json(all_news,json_file_name = "all_news.json"):
    news_dict_list = []
    for news in all_news:
        news_dict_list.append(news.to_dict())
    with open(json_file_name, 'w') as outfile:
        json.dump(news_dict_list, outfile, ensure_ascii=False, indent=4)
        
        
async def main():
    bigpara_base_url = "https://bigpara.hurriyet.com.tr"
    bigpara_news_url = bigpara_base_url + "/borsa/haber/"
    page_count = 40
    SOURCE = "BIGPARA"

    all_news = get_news_links(base_url=bigpara_base_url,news_page_url=bigpara_news_url,SOURCE=SOURCE,page_count= page_count)
    all_news = await update_news_with_content_async(all_news)
    
    save_news_to_json(all_news, json_file_name="bigpara_borsa_news.json")
    
if __name__ == "__main__":
    asyncio.run(main())