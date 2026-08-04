# Conversational AI Assistant

## Architecture
GovTrack AI integrates a decoupled RAG (Retrieval-Augmented Generation) pipeline.
It acts as a Personal Career Assistant allowing natural language queries.

## Components
- **`ILLMProvider`**: Pluggable interface for `OpenAI`, `Gemini`, `Claude`, `Ollama`, or `LMStudio`.
- **`IVectorStore`**: Embeddings database architecture.
- **`RAGEngine`**: Dynamically constructs prompts using retrieved context.
- **`CareerCoach`**: Specialized prompt templates for skill gap analysis and interview prep.
- **`ConversationMemory`**: Stateful multi-turn chat memory.
