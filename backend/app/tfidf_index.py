import os, json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

INDEX_PATH = './data/tfidf_index.pkl'
DATA_PATH = './data/reviews.json'

class TfidfIndex:
    def __init__(self, docs, ids):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=2000)
        self.vectors = self.vectorizer.fit_transform(docs)
        self.ids = ids

    def search(self, q, k=5):
        qv = self.vectorizer.transform([q])
        sims = cosine_similarity(qv, self.vectors)[0]
        pairs = sorted(list(zip(self.ids, sims)), key=lambda x: x[1], reverse=True)[:k]
        return [{"id": int(pid), "score": float(score)} for pid, score in pairs]

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
