"""
Setup RAG - Indeksowanie notatek Obsidian do Qdrant
"""
import os
from pathlib import Path
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from tqdm import tqdm
from shared.logging import setup_logging, get_logger
from shared.config import get_settings

setup_logging(level="INFO", format="console", service_name="rag-setup")
logger = get_logger(__name__)

settings = get_settings()


class VaultIndexer:
    """Indeksowanie Obsidian Vault do Qdrant"""

    def __init__(
        self,
        vault_path: Path,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "obsidian_notes"
    ):
        self.vault_path = vault_path
        self.collection_name = collection_name

        # Qdrant client
        self.qdrant = QdrantClient(url=qdrant_url)

        # Embeddings (Ollama)
        self.embeddings = OllamaEmbeddings(
            base_url=settings.ollama_host,
            model="nomic-embed-text"
        )

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )

        logger.info(
            "indexer_initialized",
            vault=str(vault_path),
            collection=collection_name
        )

    def create_collection(self, vector_size: int = 768):
        """Utwórz kolekcję w Qdrant (jeśli nie istnieje)"""
        try:
            self.qdrant.get_collection(self.collection_name)
            logger.info("collection_exists", name=self.collection_name)
        except Exception:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info("collection_created", name=self.collection_name)

    def load_documents(self) -> List[Dict]:
        """Załaduj wszystkie notatki Markdown z Vault"""
        logger.info("loading_documents", path=str(self.vault_path))

        documents = []

        for md_file in self.vault_path.rglob("*.md"):
            # Skip templates and hidden files
            if md_file.name.startswith('.') or 'templates' in md_file.parts:
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter (basic)
                metadata = {
                    'source': str(md_file.relative_to(self.vault_path)),
                    'title': md_file.stem,
                    'path': str(md_file)
                }

                # Extract tags from frontmatter if present
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        content = parts[2]

                        # Simple tag extraction
                        if 'tags:' in frontmatter:
                            tags_section = frontmatter.split('tags:')[1].split('\n')[0]
                            metadata['tags'] = tags_section.strip()

                documents.append({
                    'content': content.strip(),
                    'metadata': metadata
                })

            except Exception as e:
                logger.warning("file_read_failed", file=str(md_file), error=str(e))

        logger.info("documents_loaded", count=len(documents))
        return documents

    def index_documents(self, documents: List[Dict]):
        """Podziel dokumenty na chunki i zaindeksuj"""
        logger.info("indexing_started", doc_count=len(documents))

        points = []
        point_id = 0

        for doc in tqdm(documents, desc="Indexing"):
            # Split into chunks
            chunks = self.text_splitter.split_text(doc['content'])

            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.embeddings.embed_query(chunk)

                # Create point
                payload = {
                    **doc['metadata'],
                    'chunk': chunk,
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks)
                }

                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )

                points.append(point)
                point_id += 1

                # Batch upsert (co 100 punktów)
                if len(points) >= 100:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    points = []

        # Upsert remaining
        if points:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )

        logger.info("indexing_completed", total_chunks=point_id)

    def run(self):
        """Pełny proces indeksowania"""
        # 1. Create collection
        self.create_collection()

        # 2. Load documents
        documents = self.load_documents()

        if not documents:
            logger.warning("no_documents_found")
            return

        # 3. Index
        self.index_documents(documents)

        logger.info("rag_setup_complete")


def main():
    """Main entry point"""
    vault_path = Path(os.getenv('OBSIDIAN_VAULT_PATH', '/vault'))

    if not vault_path.exists():
        logger.error("vault_not_found", path=str(vault_path))
        return

    indexer = VaultIndexer(vault_path=vault_path)
    indexer.run()


if __name__ == "__main__":
    main()
