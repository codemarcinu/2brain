"""
Obsidian RAG Pipeline
"""
from typing import List, Union, Generator, Iterator, Optional
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    class Valves(BaseModel):
        QDRANT_URL: str = "http://qdrant:6333"
        COLLECTION_NAME: str = "obsidian_notes"
        TOP_K: int = 5
        SIMILARITY_THRESHOLD: float = 0.7
        # Ensure these are correct for the internal network
        OLLAMA_BASE_URL: str = "http://ollama:11434"
        EMBEDDING_MODEL: str = "nomic-embed-text"
        pipelines: List[str] = ["*"]

    def __init__(self):
        self.type = "filter"
        self.name = "Obsidian RAG"
        self.valves = self.Valves()
        self.qdrant = None
        self.embeddings = None
        logger.info(f"Filter '{self.name}' initialized successfully")

    async def on_startup(self):
        try:
            self.qdrant = QdrantClient(url=self.valves.QDRANT_URL)
            self.embeddings = OllamaEmbeddings(
                base_url=self.valves.OLLAMA_BASE_URL,
                model=self.valves.EMBEDDING_MODEL
            )
            logger.info(f"✅ Obsidian RAG: Qdrant and Ollama clients initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG clients: {e}")

    async def on_shutdown(self):
        pass

    def search_vault(self, query: str, top_k: int) -> List[dict]:
        if not self.qdrant or not self.embeddings:
            return []
            
        try:
            query_embedding = self.embeddings.embed_query(query)
            results = self.qdrant.query_points(
                collection_name=self.valves.COLLECTION_NAME,
                query=query_embedding,
                limit=top_k,
                score_threshold=self.valves.SIMILARITY_THRESHOLD
            ).points
            
            return [{
                'content': r.payload['chunk'],
                'source': r.payload['source']
            } for r in results]
        except Exception as e:
            logger.error(f"RAG Error: {e}")
            return []

    async def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        print(f"RAG Inlet called. User: {__user__}")
        messages = body.get("messages", [])
        if not messages:
            return body
        
        last_message = messages[-1]
        user_query = last_message.get("content", "")
        
        contexts = self.search_vault(user_query, top_k=self.valves.TOP_K)
        
        if contexts:
            context_str = "\n\n".join([
                f"[From: {ctx['source']}]\n{ctx['content']}"
                for ctx in contexts
            ])
            
            system_message = {
                "role": "system",
                "content": f"""You are an AI assistant with access to the user's Obsidian knowledge base.

Use the following context from their notes to answer.

CONTEXT FROM OBSIDIAN VAULT:
{context_str}

When referencing information from the notes, mention the source file."""
            }
            
            # Insert system message at the beginning
            body["messages"] = [system_message] + messages
            
            logger.info(f"RAG: Injected {len(contexts)} contexts for query: {user_query[:50]}...")
        
        return body

    async def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        return body

def get_pipeline():
    return Pipeline()
