"""
Custom RAG Pipeline dla Open Web UI
Wyszukiwanie semantyczne w notatkach Obsidian
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_community.embeddings import OllamaEmbeddings


class Pipeline:
    """
    Open Web UI Pipeline dla RAG w Obsidian

    Implementuje interface wymagany przez Open Web UI:
    https://docs.openwebui.com/pipelines/
    """

    class Valves(BaseModel):
        """Konfigurowalne parametry (UI w Open Web UI)"""
        QDRANT_URL: str = "http://qdrant:6333"
        COLLECTION_NAME: str = "obsidian_notes"
        TOP_K: int = 5
        SIMILARITY_THRESHOLD: float = 0.7
        OLLAMA_BASE_URL: str = "http://ollama:11434"
        EMBEDDING_MODEL: str = "nomic-embed-text"

    def __init__(self):
        self.type = "filter"  # filter, manifold, or function
        self.name = "Obsidian RAG"
        self.valves = self.Valves()

        # Initialize clients
        self.qdrant = None
        self.embeddings = None

    async def on_startup(self):
        """Called when pipeline starts"""
        self.qdrant = QdrantClient(url=self.valves.QDRANT_URL)
        self.embeddings = OllamaEmbeddings(
            base_url=self.valves.OLLAMA_BASE_URL,
            model=self.valves.EMBEDDING_MODEL
        )
        print(f"Obsidian RAG Pipeline initialized")

    async def on_shutdown(self):
        """Called when pipeline stops"""
        pass

    def search_vault(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Wyszukaj w Vault

        Args:
            query: User query
            top_k: Number of results

        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Search in Qdrant
        results = self.qdrant.search(
            collection_name=self.valves.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=self.valves.SIMILARITY_THRESHOLD
        )

        # Format results
        contexts = []
        for result in results:
            contexts.append({
                'content': result.payload['chunk'],
                'source': result.payload['source'],
                'title': result.payload['title'],
                'score': result.score
            })

        return contexts

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process incoming request (before LLM)

        This is where we inject RAG context
        """
        # Get user's last message
        messages = body.get("messages", [])
        if not messages:
            return body

        last_message = messages[-1]
        user_query = last_message.get("content", "")

        # Search vault
        contexts = self.search_vault(user_query, top_k=self.valves.TOP_K)

        if contexts:
            # Build context string
            context_str = "\n\n".join([
                f"[From: {ctx['source']}]\n{ctx['content']}"
                for ctx in contexts
            ])

            # Inject context into system message
            system_message = {
                "role": "system",
                "content": f"""You are an AI assistant with access to the user's Obsidian knowledge base.

Use the following context from their notes to answer questions. If the context doesn't contain relevant information, say so and provide a general answer.

CONTEXT FROM OBSIDIAN VAULT:
{context_str}

When referencing information from the notes, mention the source file."""
            }

            # Insert system message at the beginning
            body["messages"] = [system_message] + messages

            print(f"RAG: Injected {len(contexts)} contexts for query: {user_query[:50]}...")

        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process outgoing response (after LLM)

        Could be used to add citations or metadata
        """
        return body


# Required for Open Web UI to load the pipeline
def get_pipeline():
    return Pipeline()
