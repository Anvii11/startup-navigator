import os
import json
import re
import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.rag.embedding import EmbeddingGenerator

CHROMA_AVAILABLE = False
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class FallbackVectorStore:
    """
    A pure-Python/NumPy persistent vector store that acts as a fallback
    when ChromaDB is not installed or fails to compile.
    Saves document chunks, metadata, and vectors in a JSON file.
    """

    GENERIC_STOPWORDS = {
        "and", "the", "for", "in", "of", "to", "a", "an", "is", "or", "how", "can", "i",
        "what", "suggest", "startup", "startups", "idea", "ideas", "business", "company",
        "start", "need", "want", "find", "give", "me", "some", "best", "good", "top"
    }

    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.file_path = os.path.join(persist_dir, "fallback_db.json")
        os.makedirs(persist_dir, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"documents": {}, "vocab": None}

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        for idx, id_ in enumerate(ids):
            self.data["documents"][id_] = {
                "document": documents[idx],
                "metadata": metadatas[idx],
                "vector": embeddings[idx]
            }
        self._save()

    def set_vocab(self, vocab: Optional[Dict[str, int]]):
        self.data["vocab"] = vocab
        self._save()

    def get_vocab(self) -> Optional[Dict[str, int]]:
        return self.data.get("vocab")

    def reset(self):
        self.data = {"documents": {}, "vocab": None}
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
            except Exception:
                pass
        self._save()

    def query(self, query_text: str, query_vector: List[float], n_results: int) -> List[Dict[str, Any]]:
        results = []
        q_vec = np.array(query_vector)
        q_norm = np.linalg.norm(q_vec)

        # Extract domain-specific intent tokens (filtering generic filler words)
        raw_tokens = re.sub(r"[^a-z0-9\s₹]", " ", query_text.lower()).split()
        specific_tokens = [t for t in raw_tokens if len(t) > 1 and t not in self.GENERIC_STOPWORDS]

        # If filtering left nothing, fallback to all raw tokens
        if not specific_tokens:
            specific_tokens = [t for t in raw_tokens if len(t) > 1]

        for id_, doc_data in self.data["documents"].items():
            d_vec = np.array(doc_data["vector"])
            d_norm = np.linalg.norm(d_vec)

            if q_norm == 0 or d_norm == 0:
                vector_score = 0.0
            else:
                vector_score = float(np.dot(q_vec, d_vec) / (q_norm * d_norm))

            doc_str = (doc_data["document"] + " " + json.dumps(doc_data["metadata"])).lower()
            
            # Score specific domain token hits with bonus for category/title hits
            keyword_score = 0.0
            for t in specific_tokens:
                if t in doc_str:
                    keyword_score += 1.0
                    meta_title = str(doc_data["metadata"].get("title", "")).lower()
                    meta_cat = str(doc_data["metadata"].get("category", "")).lower()
                    meta_tags = str(doc_data["metadata"].get("tags", "")).lower()
                    if t in meta_cat or t in meta_title or t in meta_tags:
                        keyword_score += 2.0  # Strong boost for title/category/tag match

            combined_score = vector_score + (keyword_score * 0.5)

            results.append({
                "id": id_,
                "document": doc_data["document"],
                "metadata": doc_data["metadata"],
                "score": combined_score,
                "distance": 1.0 - combined_score
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:n_results]


class ArticleRetriever:
    """
    Coordinates semantic retrieval using ChromaDB or the pure-Python fallback vector store.
    """

    def __init__(self, embedding_generator: EmbeddingGenerator):
        self.settings = get_settings()
        self.embedding_generator = embedding_generator
        self.persist_dir = os.getenv("CHROMA_DB_DIR") or "chroma_data"
        self.collection_name = "articles_rag"

        self.chroma_client = None
        self.collection = None
        self.fallback_store = None

        if CHROMA_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                self.fallback_store = FallbackVectorStore(self.persist_dir)
        else:
            self.fallback_store = FallbackVectorStore(self.persist_dir)

    def reset_store(self):
        if self.collection:
            try:
                self.chroma_client.delete_collection(self.collection_name)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                pass
        if self.fallback_store:
            self.fallback_store.reset()

    def save_fallback_vocab(self, vocab: Optional[Dict[str, int]]):
        if self.fallback_store:
            self.fallback_store.set_vocab(vocab)

    def load_fallback_vocab(self) -> Optional[Dict[str, int]]:
        if self.fallback_store:
            return self.fallback_store.get_vocab()
        return None

    def add_chunks(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        if self.collection:
            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
                return
            except Exception:
                pass

        if self.fallback_store:
            self.fallback_store.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )

    def retrieve(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        fallback_vocab = self.load_fallback_vocab()
        if fallback_vocab and not self.embedding_generator._vocab:
            self.embedding_generator._vocab = fallback_vocab

        query_vector = self.embedding_generator.encode(query)[0]

        if self.collection:
            try:
                results = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=limit
                )
                retrieved = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0]
                    ids = results["ids"][0]
                    distances = results["distances"][0] if "distances" in results else [0.5] * len(docs)

                    for idx, doc in enumerate(docs):
                        similarity = 1.0 - distances[idx]
                        retrieved.append({
                            "id": ids[idx],
                            "content": doc,
                            "title": metas[idx].get("title", "Idea"),
                            "slug": metas[idx].get("slug", ""),
                            "category": metas[idx].get("category", "General"),
                            "tags": metas[idx].get("tags", ""),
                            "difficulty": metas[idx].get("difficulty", "beginner"),
                            "url": metas[idx].get("url", ""),
                            "article_id": metas[idx].get("article_id"),
                            "score": similarity
                        })
                if retrieved:
                    return retrieved
            except Exception:
                pass

        # Fallback query using domain-specific token boosting
        if self.fallback_store:
            results = self.fallback_store.query(query, query_vector, limit)
            retrieved = []
            for item in results:
                meta = item["metadata"]
                retrieved.append({
                    "id": item["id"],
                    "content": item["document"],
                    "title": meta.get("title", "Idea"),
                    "slug": meta.get("slug", ""),
                    "category": meta.get("category", "General"),
                    "tags": meta.get("tags", ""),
                    "difficulty": meta.get("difficulty", "beginner"),
                    "url": meta.get("url", ""),
                    "article_id": meta.get("article_id"),
                    "score": item["score"]
                })
            return retrieved

        return []
