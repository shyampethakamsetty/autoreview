from fastapi import FastAPI
from .api.ingest import router as ingest_router
from .api.reviews import router as reviews_router
from .api.search import router as search_router
from .api.analytics import router as analytics_router

app = FastAPI(title='Cube Assessment API')

app.include_router(ingest_router)
app.include_router(reviews_router)
app.include_router(search_router)
app.include_router(analytics_router)

@app.get('/health')
def health():
    return {'status': 'ok'}
