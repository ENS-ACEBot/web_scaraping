import unittest
import threading
import time
from ace_scraper.message_queue.RedisMessageQueue import RedisMessageQueueManager

class TestRedisMessageQueueManager(unittest.TestCase):
    def setUp(self):
        """
        setUp is called before each test method.
        Here, we instantiate our queue manager.
        Make sure Redis is running at localhost:6379 for this test.
        """
        self.queue_manager = RedisMessageQueueManager(host='localhost', port=6379, db=0)
        # You can also use a dedicated test DB like db=1 to avoid collisions with real data.

    def tearDown(self):
        """
        tearDown is called after each test method.
        It's a good place to clean up test data in Redis if needed.
        """
        # Optionally, flush the Redis DB so it doesn't affect other tests
        # WARNING: This clears ALL data in the selected DB
        self.queue_manager.redis.flushdb()

    def test_send_and_receive_message(self):
        """
        Test that sending a message to a queue is received by the consumer.
        We'll use a separate thread to listen for messages.
        """
        # A list to store received messages
        self.received_messages = []

        def callback(message):
            self.received_messages.append(message)

        # Start a thread that listens for messages on 'test_queue'
        listener_thread = threading.Thread(
            target=lambda: self.queue_manager.listen_messages("test_queue", callback),
            daemon=True  # Daemon so it won't block shutdown
        )
        listener_thread.start()

        test_message = {"text": "Hello, unittest!"}
        self.queue_manager.send_message("test_queue", test_message)

        # Wait briefly to let the listener process the message
        time.sleep(1)

        # Verify the message was received
        self.assertEqual(len(self.received_messages), 1)
        self.assertDictEqual(self.received_messages[0], test_message)

    def test_send_and_receive_string_message(self):
        """
        Test that sending a string message works as expected.
        """
        self.received_messages = []

        def callback(message):
            self.received_messages.append(message)

        listener_thread = threading.Thread(
            target=lambda: self.queue_manager.listen_messages("my_string_queue", callback),
            daemon=True
        )
        listener_thread.start()

        test_message = "Simple string message"
        self.queue_manager.send_message("my_string_queue", test_message)

        time.sleep(1)

        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], test_message)

if __name__ == '__main__':
    unittest.main()
