from fastapi import APIRouter, Header, HTTPException, Query
from typing import List
import os, json
from ..tfidf_index import TfidfIndex

router = APIRouter()
API_KEY = os.getenv('API_KEY', 'supersecret')
_index = None

@router.get('/search')
def search(q: str = Query(...), k: int = Query(5), x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    global _index
    if _index is None:
        _index = TfidfIndex.load_index()  # builds from data file if needed
    results = _index.search(q, k=k)
    return results
