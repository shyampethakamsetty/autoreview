from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List
from sqlmodel import Session
from ..models import Review
from ..db import get_session, init_db
import os

router = APIRouter()

API_KEY = os.getenv('API_KEY', 'supersecret')

@router.post('/ingest')
def ingest(reviews: List[Review], x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    init_db()
    from ..db import engine
    with Session(engine) as session:
        for r in reviews:
            session.merge(r)
        session.commit()
    return {'ingested': len(reviews)}
