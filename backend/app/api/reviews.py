from fastapi import APIRouter, Header, HTTPException, Path, Body
from typing import List, Optional
from sqlmodel import select, Session
from ..models import Review
from ..db import engine, init_db
import os

router = APIRouter()
API_KEY = os.getenv('API_KEY', 'supersecret')

@router.get('/reviews', response_model=List[Review])
def list_reviews(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    init_db()
    with Session(engine) as session:
        statement = select(Review)
        results = session.exec(statement).all()
        return results

@router.get('/reviews/{review_id}', response_model=Review)
def get_review(review_id: int = Path(...), x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    with Session(engine) as session:
        r = session.get(Review, review_id)
        if not r:
            raise HTTPException(status_code=404, detail='Not found')
        return r

@router.post('/reviews/{review_id}/suggest-reply')
def suggest_reply(review_id: int, payload: dict = Body({}), x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    # very simple stub reply generator
    with Session(engine) as session:
        r = session.get(Review, review_id)
        if not r:
            raise HTTPException(status_code=404, detail='Not found')
    reply = f"Hi — thanks for your feedback about {r.location}. We're sorry to hear you had an issue." if r.rating < 4 else f"Hi — thanks for your kind words about {r.location}!"
    return {"reply": reply, "tags": {"sentiment": r.sentiment or 'neutral', "topic": r.topic or 'general'}, "reasoning_log": ["stub"]}
