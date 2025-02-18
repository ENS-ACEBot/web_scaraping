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

## Running the Scraper
- The script can be runned in background task, 
-- nohub will be used to run task in background even terminal window is closed
-- pid of program will be saved to process.pid file

- check if the process is running
```sh
ps -p $(cat process.pid)
```
- Stop the process
```sh
kill $(cat process.pid)
```
- start the process (& is for running it at background)
```sh
nohup python3 main.py &
```


## Configuration

The configuration for the news scraper is stored in the `env/config.json` file. This file contains the paths for the log file and the database file, as well as the period time for scraping.(at the begining you should create env file)

### Example `config.json`:

```json
{
    "log_file_path": "logs/news_scraper.log",
    "db_file_path": "data/sql_news.db",
    "scrape_period_seconds": 10
}
```

### Configuration Parameters:

- `log_file_path`: The path to the log file where the scraping process logs will be saved.
- `db_file_path`: The path to the database file where the news articles will be saved.
- `scrape_period_seconds`: The period time in seconds for running the scraper. This value can be changed dynamically while the script is running.

## Updating Schedule Time

To change the period time for running the scraper dynamically, update the `scrape_period_seconds` value in the `env/config.json` file. The script will automatically adjust its period based on the new value.


## OLD NEWS DATA's DRIVE LINK
- the data is holding in the folders are moved to drive folder
- https://drive.google.com/drive/folders/1abdh1h5vi87vGi30_9c_CEC6ta4EOkjS?usp=sharing
