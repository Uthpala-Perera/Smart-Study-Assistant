from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class SimpleRAG:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.chunks = []
        self.vectors = None

    def add_documents(self, text, chunk_size=500):
        self.chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        self.vectors = self.vectorizer.fit_transform(self.chunks)

    def query(self, query_text, top_k=3):
        if self.vectors is None:
            return ""

        query_vec = self.vectorizer.transform([query_text])
        similarities = (self.vectors @ query_vec.T).toarray().flatten()

        top_indices = similarities.argsort()[-top_k:][::-1]

        return " ".join([self.chunks[i] for i in top_indices])