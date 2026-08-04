class PromptTemplates:
    RAG_SYSTEM = (
        "You are GovTrack AI, an expert career assistant. "
        "Use the provided context to answer the user's question. "
        "If the answer is not in the context, say so. Do not hallucinate."
    )
    
    @staticmethod
    def build_rag_prompt(query: str, context_docs: list[dict]) -> str:
        ctx_str = "\n---\n".join([str(d) for d in context_docs])
        return f"Context:\n{ctx_str}\n\nQuery:\n{query}\n\nAnswer:"
