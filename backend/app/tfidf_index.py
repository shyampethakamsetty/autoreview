import os, json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import redis
import hashlib
from typing import Optional

INDEX_PATH = './data/tfidf_index.pkl'
DATA_PATH = './data/reviews.json'

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(REDIS_URL)
            redis_client.ping()  # Test connection
        except:
            redis_client = None  # Fallback to no caching
    return redis_client

class TfidfIndex:
    def __init__(self, docs, ids):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=2000)
        if not docs:  # Handle empty documents case
            self.vectors = None
            self.ids = []
        else:
            self.vectors = self.vectorizer.fit_transform(docs)
            self.ids = ids

    def search(self, q, k=5):
        # Handle empty index case
        if self.vectors is None or len(self.ids) == 0:
            return []
            
        # Try to get cached results
        cache_key = f"search:{hashlib.md5(q.encode()).hexdigest()}:{k}"
        redis_client = get_redis_client()
        
        if redis_client:
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            except:
                pass  # Continue without cache
        
        # Compute search results
        qv = self.vectorizer.transform([q])
        sims = cosine_similarity(qv, self.vectors)[0]
        pairs = sorted(list(zip(self.ids, sims)), key=lambda x: x[1], reverse=True)[:k]
        results = [{"id": int(pid), "score": float(score)} for pid, score in pairs]
        
        # Cache results for 5 minutes
        if redis_client:
            try:
                redis_client.setex(cache_key, 300, json.dumps(results))
            except:
                pass  # Continue without cache
        
        return results

    @classmethod
    def load_index(cls):
        # build index from data file
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, 'rb') as f:
                return pickle.load(f)
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                data = json.load(f)
            docs = [d['text'] for d in data]
            ids = [d['id'] for d in data]
            idx = cls(docs, ids)
            with open(INDEX_PATH, 'wb') as f:
                pickle.dump(idx, f)
            return idx
        return cls([], [])
