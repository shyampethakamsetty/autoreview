from fastapi import APIRouter, Header, HTTPException
import os
from sqlmodel import Session, select
from ..models import Review
from ..db import engine

router = APIRouter()
API_KEY = os.getenv('API_KEY', 'supersecret')

@router.get('/analytics')
def analytics(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    with Session(engine) as session:
        stmt = select(Review)
        rows = session.exec(stmt).all()
    # simple counts
    counts = {}
    for r in rows:
        s = r.sentiment or 'unknown'
        counts[s] = counts.get(s, 0) + 1
    return {"counts": counts, "total": len(rows)}
