from abc import ABC, abstractmethod

class IVectorStore(ABC):
    @abstractmethod
    def add_documents(self, docs: list[dict], embeddings: list[list[float]]): pass
    
    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]: pass

class LocalVectorStore(IVectorStore):
    def __init__(self):
        self.store = []
        
    def add_documents(self, docs: list[dict], embeddings: list[list[float]]):
        for d, e in zip(docs, embeddings):
            self.store.append({'doc': d, 'emb': e})
            
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        # Mock cosine similarity return
        return [item['doc'] for item in self.store[:top_k]]
