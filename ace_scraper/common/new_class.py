from datetime import datetime

# Description: This file contains the class for the news object
# title, content, date, source, source_url
class News:
    input_date_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]  # List of possible date formats
    output_date_format = "%Y-%m-%d %H:%M:%S"  # Output date format
    
    def __init__(self, title, source, news_url, content=None, date_time=None):
        self.title = title  # string
        self.content = content  # string
        self.date_time = News.parse_date_time(date_time)  # datetime
        self.source = source  # string
        self.news_url = news_url  # string
        
    @classmethod
    def parse_date_time(self, date_time_str):
        if isinstance(date_time_str, datetime):
            return date_time_str
        
        if date_time_str is None:
            return None
        
        for date_format in self.input_date_formats:
            try:
                return datetime.strptime(date_time_str, date_format)
            except ValueError :
                print(f"Date format of '{date_time_str}' is not supported.,type = {type(date_time_str)}")
                continue
        raise ValueError(f"Date format of '{date_time_str}' is not supported.")
    
    def __str__(self) -> str:
        return f"{self.title} - {self.date_time} - {self.source}"

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content if self.content else "",
            "date_time": self.date_time.strftime(self.output_date_format),
            "source": self.source,
            "news_url": self.news_url,
        }

    @classmethod
    def from_dict(cls, data):
        # Parse `date_time` if it exists in `data`
        date_time = data.get("date_time")
        if date_time:
            # Parse date_time string to a datetime object, assuming a specific format
            date_time = News.parse_date_time(date_time)
        # Return an instance of `News` with data from the dictionary
        return cls(
            title=data.get("title"),
            content=data.get("content") if data.get("content") else "",
            date_time=date_time,
            source=data.get("source"),
            news_url=data.get("news_url"),
        )

    #   date :23.10.2024
    #   time :12:46
    def date_time_to_dateTime(date, time, date_format='%d.%m.%Y %H:%M'):
        date_str = date + " " + time
        return datetime.strptime(date_str, date_format)

    # Comparison operators with type checking

    def __eq__(self, other):
        """
        Overridden equality operator to compare news objects based on their `news_url`.
        """
        if not isinstance(other, News):
            raise TypeError("Cannot compare News with non-News instance")
        return self.news_url == other.news_url

    def __lt__(self, other):
        if not isinstance(other, News):
            raise TypeError("Cannot compare News with non-News instance")
        return self.date_time < other.date_time

    def __le__(self, other):
        if not isinstance(other, News):
            raise TypeError("Cannot compare News with non-News instance")
        return self.date_time <= other.date_time

    def __gt__(self, other):
        if not isinstance(other, News):
            raise TypeError("Cannot compare News with non-News instance")
        return self.date_time > other.date_time

    def __ge__(self, other):
        if not isinstance(other, News):
            raise TypeError("Cannot compare News with non-News instance")
        return self.date_time >= other.date_time

    def __hash__(self):
        """
        This is required for using the `News` object in sets and as dictionary keys.
        We hash by `news_url` since it's the unique identifier for the news object.
        """
        return hash(self.news_url)

    def __repr__(self):
        return f"News(title={self.title}, source={self.source}, date_time={self.date_time}, news_url={self.news_url})"
