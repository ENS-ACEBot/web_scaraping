import sqlite3
from abc import ABC, abstractmethod
#from news_database import NewsDatabase
from common.new_class import News
import logging


#class SQLLiteNewsDatabase(NewsDatabase):
class SQLLiteNewsDatabase():

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()
        logging.info("SQLLite database initialized")
     
    
    def save_news(self, news_list: list[News]) -> list[News]:
        '''
            Save a list of news to the database.
            Return saved news list.
        '''
        insert_query = '''
        INSERT INTO news(title, content,date_time,source,news_url) 
        VALUES(?,?,?,?,?);
        '''
        news_data = [(news.title, news.content, news.date_time, news.source, news.news_url) 
                     for news in news_list]
        try:
            self.cursor.executemany(insert_query, news_data)
            self.connection.commit()
            logging.info(f"Saved {len(news_list)} news to the database.")
            return news_list
        except sqlite3.IntegrityError as e:
            saved_news = []
            logging.error(f"An error occurred while saving news to the database: {e}")
            self.connection.rollback()
            # Save each news one by one in case of error
            logging.error("Trying to save each news one by one...")
            for idx,news in enumerate(news_list):
                logging.info(f"{idx+1}/{len(news_list)}")
                saved_new = self.save_new(news)
                if saved_new:
                    saved_news.append(news)
            return saved_news
        except sqlite3.Error as e:
            logging.error(f"An error occurred while saving news to the database: {e}")
            self.connection.rollback()  # Rollback the transaction in case of error
            return []

    def save_new(self, news: News):
        '''
            Save a single news to the database.
        '''
        insert_query = '''
        INSERT INTO news(title, content,date_time,source,news_url) 
        VALUES(?,?,?,?,?);
        '''
        news_data = (news.title, news.content, news.date_time, news.source, news.news_url)
        try:
            self.cursor.execute(insert_query, news_data)
            self.connection.commit()
            logging.info(f"Saved {news.news_url} to the database.")
            return news
        except sqlite3.Error as e:
            logging.debug(f"An error occurred while saving news to the database: {e}")
            self.connection.rollback()
            return None
                       
    def get_all(self) -> list[News]:
        select_query = "SELECT title, content,date_time,source,news_url FROM news;"
        self.cursor.execute(select_query)
        all_news_tuples = self.cursor.fetchall()
        
        # Convert tuples to News objects
        all_news = [News(title= title, content=content, date_time = date_time, source =source, news_url=news_url) 
                    for title, content, date_time, source, news_url in all_news_tuples]
        logging.info(f"Retrieved {len(all_news)} news from the database.")
        return all_news
        pass
    
    def get_query(self, from_date = None, to_date = None, source = None, limit: int = None) -> list[News]:
        get_query_string = "SELECT title,content,date_time,source,news_url FROM news "
        conditions = []
        
        if(from_date):
            conditions.append(f"date_time >= '{from_date}'")
        if(to_date):
            conditions.append(f"date_time <= '{to_date}'")
        if(source):
            conditions.append(f"source = '{source}'")
        
        if(conditions):
            get_query_string += "WHERE " + " AND ".join(conditions)
        
        get_query_string += " ORDER BY date_time DESC"
        
        if limit:
            get_query_string += f" LIMIT {limit}"
        
        get_query_string += ";"
        
        try:
            self.cursor.execute(get_query_string)
            news_list_tuples = self.cursor.fetchall()
            news_list = [News(title =title, content=content, date_time=date_time, source = source, news_url = news_url) 
                        for title, content, date_time, source, news_url in news_list_tuples]
            logging.debug(f"Query executed :[{get_query_string}] - {len(news_list)} news fetched")
            return news_list
        except Exception as e:
            logging.error(f"Query [{get_query_string}] couldn't executed : {e}")
            return []
        pass
    
    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            date_time TEXT,
            source TEXT,
            news_url TEXT UNIQUE
        );
        """    
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"An error occurred while creating the table: {e}")
            self.connection.rollback()
            return False
        pass 
    
    def count_news(self):
        count_query = "SELECT COUNT(*) FROM news;"
        self.cursor.execute(count_query)
        count = self.cursor.fetchone()[0]
        return count
    
    def __del__(self):
        self.connection.close()
        logging.info("SQLLite database closed !")
        
    # class variables
    # db_path: str
    # connection: sqlite3.Connection
    # cursor: sqlite3.Cursor
    
