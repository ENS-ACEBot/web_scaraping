import sqlite3
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import os

def fetch_news_data(db_path='ace_scraper/data/sql_news.db'):
    """Fetches source and date fields from the news database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT source, date FROM news")
    data = cursor.fetchall()
    conn.close()
    return data

def count_news_per_source(data):
    """Counts how many news articles exist for each source."""
    sources = [row[0] for row in data if row[0]]
    return Counter(sources)

def count_news_per_year(data):
    """Counts how many news articles exist for each year."""
    years = []
    for _, date_str in data:
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                years.append(dt.year)
            except ValueError:
                continue
    return Counter(years)

def ensure_graphs_folder():
    """Ensure the 'graphs' folder exists."""
    os.makedirs('graphs', exist_ok=True)

def plot_bar_chart(counter, title, xlabel, ylabel, filename):
    """Plots and saves a bar chart from the given Counter data."""
    labels = list(counter.keys())
    values = list(counter.values())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = os.path.join('ace_scraper/graph_generator/graphs', filename)
    plt.savefig(output_path)
    print(f"Saved chart as: {output_path}")
    plt.show()

def main():
    ensure_graphs_folder()

    data = fetch_news_data()

    source_counts = count_news_per_source(data)
    year_counts = count_news_per_year(data)

    plot_bar_chart(
        source_counts,
        'Number of News per Source',
        'Source',
        'Number of News',
        'news_per_source.png'
    )

    plot_bar_chart(
        year_counts,
        'Number of News per Year',
        'Year',
        'Number of News',
        'news_per_year.png'
    )

if __name__ == '__main__':
    main()
