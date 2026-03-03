from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    date_posted: Optional[str] = None
    skills: Optional[List[str]] = None
    salary: Optional[str] = None

    def to_dict(self):
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "date_posted": self.date_posted,
            "skills": self.skills,
            "salary": self.salary
        }
