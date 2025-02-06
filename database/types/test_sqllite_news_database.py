import unittest
from sqllite_news_database import SQLLiteNewsDatabase
from new_class import News

class TESTSQLLiteNewsDatabase(unittest.TestCase):
    def setUp(self):
        # set up temporary database
        self.db_path = "test.db"
        self.db = SQLLiteNewsDatabase(self.db_path)
        self.db.create_table()
    
    def tearDown(self):
        # delete temporary database
        #delete table query 
        delete_table_query = "DROP TABLE news;"
        self.db.cursor.execute(delete_table_query)
        self.db.connection.close()
        return
    
    def test_save_news(self):
        news_list = [
            News(title="Title 1", content="Content 1", date_time="2024-01-01 10:19", source="Source 1", news_url="http://example.com/1"),
            News(title="Title 2", content="Content 2", date_time="2024-01-02 10:19", source="Source 2", news_url="http://example.com/2")
        ]
        result = self.db.save_news(news_list=news_list)
        self.assertTrue(result)
        all_news = self.db.get_all()
        self.assertEqual(len(all_news),2)
        
    
    def test_get_query(self):
        news_list = [
            News(title="Title 1", content="Content 1", date_time="2024-01-01 10:19", source="Source 1", news_url="http://example.com/1"),
            News(title="Title 2", content="Content 2", date_time="2024-01-02 10:19", source="Source 2", news_url="http://example.com/2"),
            News(title="Title 3", content="Content 3", date_time="2024-01-03 10:19", source="Source 1", news_url="http://example.com/3")
        ]
        self.db.save_news(news_list=news_list)
        
        # Query for news from Source 1 between 2024-01-01 and 2024-01-02
        queried_news = self.db.get_query(from_date="2024-01-01", to_date="2024-01-02", source="Source 1")
        self.assertEqual(len(queried_news), 1)
        self.assertEqual(queried_news[0].title, "Title 1")
        
        # Query for news from Source 2
        queried_news = self.db.get_query(from_date=None, to_date=None, source="Source 2")
        self.assertEqual(len(queried_news), 1)
        self.assertEqual(queried_news[0].title, "Title 2")
        
        # Query for all news between 2024-01-01 and 2024-01-04
        queried_news = self.db.get_query(from_date="2024-01-01", to_date="2024-01-04", source=None)
        self.assertEqual(len(queried_news), 3)
        
if __name__ == '__main__':
    unittest.main()