import sqlite3
from abc import ABC, abstractmethod
#from news_database import NewsDatabase
from new_class import News
import logging


#class SQLLiteNewsDatabase(NewsDatabase):
class SQLLiteNewsDatabase():

    """
    Abstract base class for a news database.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_table()
        logging.info("SQLLite database initialized")
     
    def save_news(self, news_list: list[News]):
        insert_query = '''
        INSERT INTO news(title, content,date,source,news_url) 
        VALUES(?,?,?,?,?);
        '''
        news_data = [(news.title, news.content, news.date_time, news.source, news.news_url) 
                     for news in news_list]
        try:
            self.cursor.executemany(insert_query, news_data)
            self.connection.commit()
            logging.info(f"Saved {len(news_list)} news to the database.")
        except sqlite3.Error as e:
            logging.error(f"An error occurred while saving news to the database: {e}")
            self.connection.rollback()  # Rollback the transaction in case of error
            return False
        return True

    def get_all(self) -> list[News]:
        select_query = "SELECT * FROM news;"
        self.cursor.execute(select_query)
        all_news_tuples = self.cursor.fetchall()
        
        # Convert tuples to News objects
        all_news = [News(title, content, date_time, source, news_url) 
                    for id, title, content, date_time, source, news_url in all_news_tuples]
        logging.info(f"Retrieved {len(all_news)} news from the database.")
        return all_news
        pass
    
    def get_query(self, from_date : str, to_date : str, source : str) -> list[News]:
        get_query_string = "SELECT * FROM news "
        if(from_date != None or to_date != None or source != None):
            get_query_string+= "WHERE "
            if(from_date != None):
                get_query_string += f"date >= \"{from_date}\" "
            if(to_date != None):
                if(from_date !=None):
                    get_query_string +="AND "
                get_query_string += f"date <=\"{to_date}\" "
            if(source != None):
                if(from_date !=None or to_date != None):
                    get_query_string +="AND "
                get_query_string += f"source = \"{source}\" "
                
        get_query_string +=";"
        try:
            self.cursor.execute(get_query_string)
            news_list_tuples = self.cursor.fetchall()
            news_list = [News(title, content, date_time, source, news_url) 
                        for id, title, content, date_time, source, news_url in news_list_tuples]
            logging.info(f"Query executed :[{get_query_string}] - {len(news_list)} news fetched")
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
            date TEXT,
            source TEXT,
            news_url TEXT
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
    
    def __del__(self):
        self.connection.close()
        logging.info("SQLLite database closed !")
        
    # class variables
    # db_path: str
    # connection: sqlite3.Connection
    # cursor: sqlite3.Cursor
    
