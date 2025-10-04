from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List
from sqlmodel import Session
from ..models import Review
from ..db import get_session, init_db
from .. import ai_client
from datetime import datetime, date
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

API_KEY = os.getenv('API_KEY', 'supersecret')

@router.post('/ingest')
def ingest(reviews: List[Review], x_api_key: str = Header(None), enrich: bool = True):
    """Ingest reviews with optional AI enrichment for sentiment and topics"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    # Validate required fields for each review
    for i, review in enumerate(reviews):
        missing_fields = []
        if not hasattr(review, 'rating') or review.rating is None:
            missing_fields.append('rating')
        if not hasattr(review, 'text') or not review.text:
            missing_fields.append('text')
        if not hasattr(review, 'date') or review.date is None:
            missing_fields.append('date')
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f'Review {i}: Missing required fields: {", ".join(missing_fields)}'
            )
    
    init_db()
    from ..db import engine
    
    enriched_count = 0
    with Session(engine) as session:
        for r in reviews:
            # Convert string date to date object if needed
            if isinstance(r.date, str):
                r.date = datetime.strptime(r.date, '%Y-%m-%d').date()
            
            # Auto-compute sentiment and topic if not provided and enrich=True
            if enrich:
                if not r.sentiment:
                    try:
                        r.sentiment = ai_client.analyze_sentiment(r.text)
                        enriched_count += 1
                    except Exception as e:
                        logger.error(f"Failed to analyze sentiment for review {r.id}: {e}")
                        r.sentiment = 'neutral'
                
                if not r.topic:
                    try:
                        r.topic = ai_client.extract_topic(r.text)
                    except Exception as e:
                        logger.error(f"Failed to extract topic for review {r.id}: {e}")
                        r.topic = 'general'
            
            session.merge(r)
        session.commit()
    
    return {
        'ingested': len(reviews),
        'enriched': enriched_count if enrich else 0,
        'message': f'Successfully ingested {len(reviews)} reviews' + (f' ({enriched_count} enriched with AI)' if enrich else '')
    }
