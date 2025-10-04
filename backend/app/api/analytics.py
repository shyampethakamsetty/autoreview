from fastapi import APIRouter, Header, HTTPException
import os
from sqlmodel import Session, select
from ..models import Review
from ..db import engine
from collections import defaultdict

router = APIRouter()
API_KEY = os.getenv('API_KEY', 'supersecret')

@router.get('/analytics')
def analytics(x_api_key: str = Header(None)):
    """Get analytics with sentiment and topic breakdowns"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    with Session(engine) as session:
        stmt = select(Review)
        rows = session.exec(stmt).all()
    
    # Aggregate counts
    sentiment_counts = defaultdict(int)
    topic_counts = defaultdict(int)
    location_counts = defaultdict(int)
    rating_counts = defaultdict(int)
    
    total_rating = 0
    
    for r in rows:
        sentiment_counts[r.sentiment or 'unknown'] += 1
        topic_counts[r.topic or 'unknown'] += 1
        location_counts[r.location] += 1
        rating_counts[str(r.rating)] += 1
        total_rating += r.rating
    
    avg_rating = round(total_rating / len(rows), 2) if rows else 0
    
    return {
        "total": len(rows),
        "average_rating": avg_rating,
        "sentiment_counts": dict(sentiment_counts),
        "topic_counts": dict(topic_counts),
        "location_counts": dict(location_counts),
        "rating_distribution": dict(rating_counts)
    }
