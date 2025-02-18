# News Scraper

This project is a news scraper that collects news articles from various sources and saves them to a SQLite database. The scraper runs periodically and logs the scraping process.

## Sources 
- https://www.kap.org.tr/
- https://bigpara.hurriyet.com.tr/
- https://finans.mynet.com/

## Features
- Scrapes news articles from multiple sources for given time interval
- Saves news articles to a SQLite/Postgresql/Json database
- Logs the scraping process
- Runs periodically using 

## Requirements


## Setup

1. Clone the repository:

```sh
git clone https://github.com/yourusername/news-scraper.git
cd news-scraper
```

2. Create a virtual environment and activate it:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:
```sh
pip install -r requirements.txt
```

4. Create data and log folder for database and logger:
```sh
mkdir data 
mkdir logs
```


## Running the Scraper
```sh
python main.py
```

## Configuration
- The SQLite database is located at data/sql_news.db.

## OLD NEWS DATA's DRIVE LINK
- the data is holding in the folders are moved to drive folder
- https://drive.google.com/drive/folders/1abdh1h5vi87vGi30_9c_CEC6ta4EOkjS?usp=sharing
