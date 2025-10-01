from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date

class Review(SQLModel, table=True):
    id: int = Field(primary_key=True)
    location: str
    rating: int
    text: str
    date: date
    sentiment: Optional[str] = None
    topic: Optional[str] = None
