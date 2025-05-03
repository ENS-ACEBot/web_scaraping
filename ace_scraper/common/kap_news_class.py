
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


'''
==========================================================================================
DataClass Documentation
==========================================================================================
The `dataclass` module in Python provides a decorator (`@dataclass`) that simplifies the 
creation of classes primarily used for storing data. It automatically generates boilerplate 
methods like `__init__`, `__repr__`, `__eq__`, and more, making it easier to manage objects 
without manually writing these methods.

==========================================================================================
'''

@dataclass
class KapNews:
    publish_date: Optional[datetime]
    kap_title: Optional[str]
    is_old_kap: Optional[bool]
    disclosure_class: Optional[str]
    disclosure_type: Optional[str]
    disclosure_category: Optional[str]
    summary: Optional[str]
    subject: Optional[str]
    rule_type_term: Optional[str]
    disclosure_index: Optional[int]
    is_late: Optional[bool]
    stock_codes: Optional[str]
    has_multi_language_support: Optional[bool]
    attachment_count: Optional[int]
    content: Optional[str]
    @classmethod
    def special_strptime(cls, date_str: str) -> Optional[datetime]:
        """
        Convert a date string to a datetime object, handling special cases for 'Dün' and 'Bugün'.

        This method was created to handle specific date formats encountered in the data source.
        The data source sometimes uses the terms 'Dün' (yesterday) and 'Bugün' (today) instead
        of explicit dates. This method replaces 'Dün' with yesterday's date and 'Bugün' with
        today's date while preserving the time component. This ensures that the date strings
        are correctly parsed into datetime objects for further processing.

        Parameters:
        date_str (str): The date string to be converted.

        Returns:
        Optional[datetime]: The corresponding datetime object, or None if parsing fails.
        """
        try:
            if "Dün" in date_str:
                date_str = date_str.replace("Dün", (datetime.now() - timedelta(days=1)).strftime("%d.%m.%y"))
            elif "Bugün" in date_str:
                date_str = date_str.replace("Bugün", datetime.now().strftime("%d.%m.%y"))
            return KapNews.parse_date_time(date_str) if date_str else None
        except ValueError as e:
            print(f"Error parsing date: {e}")
            return None

    @classmethod
    def parse_date_time(self, date_time_str):
        if isinstance(date_time_str, datetime):
            return date_time_str
        
        if date_time_str is None:
            return None
        
        for date_format in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
            try:
                return datetime.strptime(date_time_str, date_format)
            except ValueError :
                print(f"Date format of '{date_time_str}' is not supported.,type = {type(date_time_str)}")
                continue
        raise ValueError(f"Date format of '{date_time_str}' is not supported.")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Convert a dictionary to a KapNews object.
        Handles the date conversion for publishDate.
        """
        return cls(
            publish_date=cls.special_strptime(data["publishDate"]) if data.get("publishDate") else None,
            kap_title=data.get("kapTitle"),
            is_old_kap=data.get("isOldKap"),
            disclosure_class=data.get("disclosureClass"),
            disclosure_type=data.get("disclosureType"),
            disclosure_category=data.get("disclosureCategory"),
            summary=data.get("summary"),
            subject=data.get("subject"),
            rule_type_term=data.get("ruleTypeTerm"),
            disclosure_index=data.get("disclosureIndex"),
            is_late=data.get("isLate"),
            stock_codes=data.get("stockCodes"),
            has_multi_language_support=data.get("hasMultiLanguageSupport"),
            attachment_count=data.get("attachmentCount"),
            content = data.get("content")
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the KapNews object to a dictionary.
        Ensures publish_date is serialized back to string format.
        """
        return {
            "publishDate": self.publish_date.strftime("%d.%m.%y %H:%M") if self.publish_date else None,
            "kapTitle": self.kap_title,
            "isOldKap": self.is_old_kap,
            "disclosureClass": self.disclosure_class,
            "disclosureType": self.disclosure_type,
            "disclosureCategory": self.disclosure_category,
            "summary": self.summary,
            "subject": self.subject,
            "ruleTypeTerm": self.rule_type_term,
            "disclosureIndex": self.disclosure_index,
            "isLate": self.is_late,
            "stockCodes": self.stock_codes,
            "hasMultiLanguageSupport": self.has_multi_language_support,
            "attachmentCount": self.attachment_count,
            "content": self.content
        }