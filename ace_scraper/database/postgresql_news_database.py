import psycopg2
from psycopg2 import sql
from psycopg2.errors import UniqueViolation
from abc import ABC, abstractmethod
from new_class import News
import logging
from urllib.parse import urlparse


class PostgresqlNewsDatabase:

    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.connection = psycopg2.connect(**self.conn_params)
        self.connection.autocommit = False  # Use explicit transactions
        self.cursor = self.connection.cursor()
        self.create_table()
        logging.info("PostgreSQL database initialized")
    
    @classmethod
    def from_url(cls, db_url: str):
        result = urlparse(db_url)
        return cls(
            dbname=result.path[1:],  # Remove leading '/'
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
    def save_news(self, news_list: list[News]):
        insert_query = sql.SQL('''
            INSERT INTO news(title, content, date_time, source, news_url) 
            VALUES (%s, %s, %s, %s, %s)
        ''')
        
        news_data = [(news.title, news.content, news.date_time, news.source, news.news_url)
                     for news in news_list]
        
        try:
            self.cursor.executemany(insert_query, news_data)
            self.connection.commit()
            logging.info(f"Saved {len(news_list)} news to the database.")
        except UniqueViolation as e:
            logging.error(f"Duplicate news found: {e}")
            self.connection.rollback()
            logging.info("Trying to save each news individually...")
            success_count = 0
            for news in news_list:
                if self.save_new(news):
                    success_count += 1
            logging.info(f"Successfully saved {success_count}/{len(news_list)} news")
            return success_count > 0
        except Exception as e:
            logging.error(f"Error saving news: {e}")
            self.connection.rollback()
            return False
        return True

    def save_new(self, news: News) -> bool:
        insert_query = sql.SQL('''
            INSERT INTO news(title, content, date_time, source, news_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (news_url) DO NOTHING
        ''')
        
        news_data = (news.title, news.content, news.date_time, news.source, news.news_url)
        
        try:
            self.cursor.execute(insert_query, news_data)
            self.connection.commit()
            if self.cursor.rowcount > 0:
                logging.info(f"Saved {news.title}")
                return True
            logging.info(f"Skipped duplicate: {news.title}")
            return False
        except Exception as e:
            logging.error(f"Error saving news {news.title}: {e}")
            self.connection.rollback()
            return False

    def get_all(self) -> list[News]:
        select_query = "SELECT title, content, date_time, source, news_url FROM news;"
        self.cursor.execute(select_query)
        return self._parse_news_results()

    def get_query(self, from_date=None, to_date=None, source=None, limit: int = None) -> list[News]:
        query = sql.SQL("SELECT title, content, date_time, source, news_url FROM news")
        conditions = []
        params = []

        if from_date:
            conditions.append(sql.SQL("date_time >= %s"))
            params.append(from_date)
        if to_date:
            conditions.append(sql.SQL("date_time <= %s"))
            params.append(to_date)
        if source:
            conditions.append(sql.SQL("source = %s"))
            params.append(source)

        if conditions:
            query = query + sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)

        query = query + sql.SQL(" ORDER BY date_time DESC")

        if limit:
            query = query + sql.SQL(" LIMIT %s")
            params.append(limit)

        try:
            self.cursor.execute(query, params)
            return self._parse_news_results()
        except Exception as e:
            logging.error(f"Query failed: {e}")
            return []

    def _parse_news_results(self) -> list[News]:
        news_tuples = self.cursor.fetchall()
        return [News(title=row[0], content=row[1], date_time=row[2],
                source=row[3], news_url=row[4]) for row in news_tuples]

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date_time TIMESTAMP NOT NULL,
            source TEXT NOT NULL,
            news_url TEXT UNIQUE NOT NULL
        );
        '''
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logging.info("Table created/verified")
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            self.connection.rollback()

    def __del__(self):
        if self.connection:
            self.connection.close()
            logging.info("PostgreSQL connection closed")