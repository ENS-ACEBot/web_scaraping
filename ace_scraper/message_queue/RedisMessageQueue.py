import redis
import json
import logging


class RedisMessageQueueManager:
    """
    A Redis-based message queue manager that can work with multiple queues.
    """
    def __init__(self, host='localhost', port=6379, db=0, queue_name='news_queue'):
        """
        Initialize the Redis connection.
        
        Parameters:
            host (str): The Redis server host.
            port (int): The Redis server port.
            db (int): The Redis database number.
            queue_name (str): The name of the queue to use.
        """
        self.queue_name = queue_name
        self.redis = redis.Redis(host=host, port=port, db=db)
        logging.info("Connected to Redis server at %s:%s, db=%s", host, port, db)
    
    def send_message(self, message):
        """
        Send a message to the specified queue.
        
        Parameters:
            message (dict or str): The message to send. If it's a dict, it will be converted to JSON.
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        self.redis.lpush(self.queue_name, message)
        logging.info("Message sent to queue '%s': %s", self.queue_name, message)
    
    def listen_messages(self, callback):
        """
        Listen for messages on the specified queue and process them with the callback.
        
        Parameters:
            queue_name (str): The name of the queue.
            callback (function): A function that processes the message.
        """
        logging.info("Listening for messages on queue '%s'...", self.queue_name)
        while True:
            # BRPOP blocks until a message is available on the queue.
            _, raw_message = self.redis.brpop(self.queue_name)
            try:
                message_str = raw_message.decode('utf-8')
            except Exception:
                message_str = raw_message
            try:
                message_obj = json.loads(message_str)
            except json.JSONDecodeError:
                message_obj = message_str
            logging.info("Received message from queue '%s': %s", self.queue_name, message_obj)
            callback(message_obj)