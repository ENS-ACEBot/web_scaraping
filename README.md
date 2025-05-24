# News Scraper

This project is a news scraper that collects news articles from various sources and saves them to a database. The scraper runs periodically and logs the scraping process.

## Sources 
- https://www.kap.org.tr/
- https://bigpara.hurriyet.com.tr/
- https://finans.mynet.com/
- https://www.bloomberght.com/

## Features
- Scrapes news articles from multiple sources for given time interval
- Supports multiple database backends (SQLite, PostgreSQL, JSON)
- Real-time data collection and historical data analysis
- Message queue integration for distributed processing
- Data visualization capabilities
- Comprehensive logging system
- Docker support for easy deployment
- Redis integration for caching and message queuing

## Requirements
- Python 3.8+
- PostgreSQL (optional, for PostgreSQL backend)
- Redis (optional, for message queuing and caching)

## Setup

1. Clone the repository:
```sh
git clone https://github.com/yourusername/news-scraper.git
cd news-scraper
```

2. Create a virtual environment and activate it:
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

3. Install the required packages:
```sh
pip install -r requirements.txt
```

4. Create the necessary directories:
```sh
mkdir -p ace_scraper/env ace_scraper/logs ace_scraper/data ace_scraper/pid
```

## Running the Scraper

### Manual Setup

1. Start the scraper:
```sh
python3 ace_scraper/main.py &
```


## Configuration

The configuration for the news scraper is stored in the `ace_scraper/env/config.json` file. This file contains various settings for the scraper.

### Example `config.json`:
```json
{
    "log_file_path": "logs/news_scraper.log",
    "db_file_path": "data/sql_news.db",
    "scrape_period_seconds": 10,

    "redis_host" : "localhost",
    "redis_port" : 6379,
    "redis_db" : 0,
    "redis_news_message_queue" : "news_queue"
}
```

### Configuration Parameters:
- `log_file_path`: Path to the log file
- `db_file_path`: Path to the database file (for SQLite)
- `scrape_period_seconds`: Scraping interval in seconds
- `database`: Database configuration (type, host, port, etc.)
- `redis`: Redis configuration for message queuing and caching

## Project Structure
```
ace_scraper/
├── data/               # Data storage
├── env/               # Configuration files
├── graph_generator/   # Data visualization tools
├── logs/              # Log files
├── message_queue/     # Message queue implementation
├── scrapers/          # Source-specific scrapers
├── database/          # Database implementations
└── common/            # Shared utilities
```

