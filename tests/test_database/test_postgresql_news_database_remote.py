import unittest
from new_class import News
from postgresql_news_database import PostgresqlNewsDatabase
import psycopg2

'''
external test url -> in config file
'''

class TestPostgresqlNewsDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # db_url = in config file 
        cls.db = PostgresqlNewsDatabase.from_url(db_url=db_url)
        
        # Clear any existing test data
        cls.db.cursor.execute("DELETE FROM news;")
        cls.db.connection.commit()
        
    @classmethod
    def tearDownClass(cls):
        print("test_postgresql_news_database_remote.py: tearDown")
        # Clean up test database
        cls.db.cursor.execute("DROP TABLE IF EXISTS news;")
        cls.db.connection.commit()
        cls.db.connection.close()
        
    def setUp(self):
        # Clear any existing test data before each test
        self.db.cursor.execute("DELETE FROM news;")
        self.db.connection.commit()

    def test_save_news(self):
        print("test_save_news started")
        news_list = [
            News(title="Title 1", content="Content 1", 
                 date_time="2024-01-01 10:19:00", source="Source 1", 
                 news_url="http://example.com/1"),
            News(title="Title 2", content="Content 2", 
                 date_time="2024-01-02 10:19:00", source="Source 2", 
                 news_url="http://example.com/2")
        ]
        
        # Test successful save
        result = self.db.save_news(news_list=news_list)
        self.assertTrue(result)
        
        # Verify data persistence
        all_news = self.db.get_all()
        self.assertEqual(len(all_news), 2)
        print("test_save_news end")


    def test_get_query(self):
        print("test_get_query started")
        news_list = [
            News(title="Title 1", content="Content 1", 
                 date_time="2024-01-01 10:19:00", source="Source 1", 
                 news_url="http://example.com/1"),
            News(title="Title 2", content="Content 2", 
                 date_time="2024-01-02 10:19:00", source="Source 2", 
                 news_url="http://example.com/2"),
            News(title="Title 3", content="Content 3", 
                 date_time="2024-01-03 10:19:00", source="Source 1", 
                 news_url="http://example.com/3")
        ]
        self.db.save_news(news_list=news_list)

        # Test date range + source filter
        queried_news = self.db.get_query(
            from_date="2024-01-01 00:00:00",
            to_date="2024-01-02 23:59:59",
            source="Source 1"
        )
        self.assertEqual(len(queried_news), 1)
        self.assertEqual(queried_news[0].title, "Title 1")

        # Test source filter
        queried_news = self.db.get_query(source="Source 2")
        self.assertEqual(len(queried_news), 1)
        self.assertEqual(queried_news[0].title, "Title 2")

        # Test date range
        queried_news = self.db.get_query(
            from_date="2024-01-01 00:00:00",
            to_date="2024-01-04 23:59:59"
        )
        self.assertEqual(len(queried_news), 3)
        print("test_get_query end")

    def test_duplicate_handling(self):
        print("test_duplicate_handling started")
        news = News(title="Dupe", content="Content", 
                   date_time="2024-01-01 10:19:00", 
                   source="Source", news_url="http://unique.com")
        
        # First insert should succeed
        self.assertTrue(self.db.save_new(news))
        
        # Second insert should fail gracefully
        self.assertFalse(self.db.save_new(news))
        
        # Should only have one record
        self.assertEqual(len(self.db.get_all()), 1)
        print("test_duplicate_handling end")

if __name__ == '__main__':
    unittest.main()