from assistant.llm_providers import ILLMProvider
from assistant.vector_db import IVectorStore
from assistant.prompts import PromptTemplates

class RAGEngine:
    def __init__(self, llm: ILLMProvider, vdb: IVectorStore):
        self.llm = llm
        self.vdb = vdb
        
    def query(self, user_query: str) -> str:
        emb = self.llm.get_embeddings(user_query)
        context = self.vdb.search(emb, top_k=3)
        prompt = PromptTemplates.build_rag_prompt(user_query, context)
        return self.llm.generate(prompt, PromptTemplates.RAG_SYSTEM)
