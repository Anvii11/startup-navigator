import sys
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.article import Article, ArticleStatus
from app.rag.embedding import EmbeddingGenerator
from app.rag.retriever import ArticleRetriever

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 200) -> List[str]:
    """
    Splits text content into overlapping chunks on natural boundaries.
    """
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
            
        limit = max(start, end - 150)
        break_pos = text.rfind("\n\n", limit, end)
        if break_pos == -1:
            break_pos = text.rfind("\n", limit, end)
        if break_pos == -1:
            break_pos = text.rfind(". ", limit, end)
        if break_pos == -1:
            break_pos = text.rfind(" ", limit, end)
            
        if break_pos != -1:
            if text[break_pos:break_pos+2] == ". ":
                end = break_pos + 1
            else:
                end = break_pos + 1
                
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - chunk_overlap
        if start < 0:
            start = 0
            
    return chunks


def _build_rich_chunk(chunk_body: str, article, category_name: str) -> str:
    """
    Embeds rich metadata preamble into each document chunk for high precision retrieval.
    Includes Title, Industry Category, Difficulty, Tags, and full text snippet.
    """
    tags_str = ", ".join(article.tags) if article.tags else ""
    difficulty = article.difficulty.value if hasattr(article.difficulty, "value") else str(article.difficulty)

    preamble = (
        f"Title: {article.title}\n"
        f"Industry/Category: {category_name}\n"
        f"Difficulty: {difficulty}\n"
        f"Keywords: {tags_str}\n"
        f"Summary: {article.summary or ''}\n\n"
    )
    return preamble + chunk_body


def rebuild_vector_index():
    """
    Queries the database for all published startup & manufacturing ideas,
    chunks them, computes vectors, and stores them in vector DB.
    """
    print("Initializing RAG Ingestion Pipeline...")
    db = SessionLocal()
    embedding_generator = EmbeddingGenerator()
    retriever = ArticleRetriever(embedding_generator)

    try:
        stmt = (
            select(Article)
            .where(Article.status == ArticleStatus.published)
            .options(selectinload(Article.category))
        )
        articles = db.scalars(stmt).all()
        print(f"Loaded {len(articles)} published startup & manufacturing ideas from database.")

        if not articles:
            print("No published ideas found. Indexing skipped.")
            return

        ids = []
        documents = []
        metadatas = []

        chunk_count = 0
        for article in articles:
            category_name = article.category.name if article.category else "General"
            tags_str = ",".join(article.tags) if article.tags else ""
            difficulty = article.difficulty.value if hasattr(article.difficulty, "value") else str(article.difficulty)

            chunks = chunk_text(article.content)
            
            for chunk_idx, chunk in enumerate(chunks):
                rich_chunk_text = _build_rich_chunk(chunk, article, category_name)
                chunk_id = f"art_{article.id}_chunk_{chunk_idx}"
                ids.append(chunk_id)
                documents.append(rich_chunk_text)
                metadatas.append({
                    "article_id": article.id,
                    "title": article.title,
                    "slug": article.slug,
                    "category": category_name,
                    "tags": tags_str,
                    "difficulty": difficulty,
                    "url": f"/articles/{article.slug}"
                })
                chunk_count += 1

        print(f"Created {chunk_count} total text chunks for index.")

        # Train fallback vocab on all document chunks for offline/keyless environments
        embedding_generator.build_vocab(documents)
        retriever.save_fallback_vocab(embedding_generator._vocab)

        # Clear existing collections
        print("Clearing existing vector index...")
        retriever.reset_store()

        # Compute vectors in batches
        print("Generating embeddings and writing to vector database...")
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_docs = documents[i : i + batch_size]
            batch_metas = metadatas[i : i + batch_size]
            
            batch_embeddings = embedding_generator.encode(batch_docs)
            
            retriever.add_chunks(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=batch_embeddings
            )
            print(f"Indexed batch {i // batch_size + 1}/{(len(documents) - 1) // batch_size + 1}...")

        print("RAG Ingestion successfully completed and index persists!")

    finally:
        db.close()

if __name__ == "__main__":
    rebuild_vector_index()
