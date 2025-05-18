# News Scraper

This project is a news scraper that collects news articles from various sources and saves them to a database. The scraper runs periodically and logs the scraping process.

## Sources 
- https://www.kap.org.tr/
- https://bigpara.hurriyet.com.tr/
- https://finans.mynet.com/
- https://www.bloomberght.com/
- https://www.aa.com.tr/

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

### Using Docker
```sh
docker-compose up -d
```

### Manual Setup
1. Navigate to the ace_scraper directory:
```sh
cd ace_scraper
```

2. Start the scraper in the background:
```sh
nohup python3 main.py &
```

3. Check if the process is running:
```sh
ps -p $(cat pid/process.pid)
```

4. Stop the process:
```sh
kill $(cat pid/process.pid)
```

## Configuration

The configuration for the news scraper is stored in the `ace_scraper/env/config.json` file. This file contains various settings for the scraper.

### Example `config.json`:
```json
{
    "log_file_path": "logs/news_scraper.log",
    "db_file_path": "data/sql_news.db",
    "scrape_period_seconds": 10,
    "database": {
        "type": "sqlite",  // or "postgresql"
        "host": "localhost",
        "port": 5432,
        "database": "news_db",
        "user": "user",
        "password": "password"
    },
    "redis": {
        "host": "localhost",
        "port": 6379
    }
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

## Historical Data
Historical news data is available at:
https://drive.google.com/drive/folders/1abdh1h5vi87vGi30_9c_CEC6ta4EOkjS?usp=sharing

## Development
- Run tests: `python -m pytest tests/`
- Check code style: `flake8 ace_scraper/`
