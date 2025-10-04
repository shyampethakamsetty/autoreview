from fastapi import APIRouter, Header, HTTPException, Query, Request
from typing import List
import os, json
from ..tfidf_index import TfidfIndex
from ..middleware import limiter, SEARCH_RATE_LIMIT

router = APIRouter()
API_KEY = os.getenv('API_KEY', 'supersecret')
_index = None

@router.get('/search')
@limiter.limit(SEARCH_RATE_LIMIT)
def search(request: Request, q: str = Query(...), k: int = Query(5), x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    global _index
    if _index is None:
        _index = TfidfIndex.load_index()  # builds from data file if needed
    results = _index.search(q, k=k)
    return results
