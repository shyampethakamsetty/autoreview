from typing import Optional, Union
from sqlmodel import SQLModel, Field
from datetime import date
from pydantic import field_validator

class Review(SQLModel, table=True):
    id: int = Field(primary_key=True)
    location: str
    rating: int
    text: str
    date: date
    sentiment: Optional[str] = None
    topic: Optional[str] = None

    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            from datetime import datetime
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v
