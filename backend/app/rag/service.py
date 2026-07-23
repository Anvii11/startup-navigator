import time
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.search_log import SearchLog
from app.rag.embedding import EmbeddingGenerator
from app.rag.retriever import ArticleRetriever
from app.rag.provider import get_llm_provider

# Minimum cosine similarity score for a retrieved chunk to be included in context.
MIN_RELEVANCE_SCORE = 0.0


class RAGService:
    @staticmethod
    def query_assistant(
        db: Session,
        question: str,
        session_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # ── Step 1: Retrieval ─────────────────────────────────────────────
        embedding_generator = EmbeddingGenerator()
        retriever = ArticleRetriever(embedding_generator)

        retrieved_chunks = retriever.retrieve(question, limit=10)
        retrieved_chunks = [
            c for c in retrieved_chunks
            if c.get("score", 0.0) >= MIN_RELEVANCE_SCORE
        ]

        # ── Step 1.5: Group & filter by industry domain ───────────────────
        merged_ideas = RAGService._merge_chunks_by_article(retrieved_chunks, question)

        # ── Step 2: Context Building ──────────────────────────────────────
        context_str = ""
        sources = []
        retrieved_ids = []

        for idx, idea in enumerate(merged_ideas[:5]):
            tags_display = idea.get("tags", "")
            if isinstance(tags_display, list):
                tags_display = ", ".join(tags_display)

            context_str += (
                f"--- SOURCE {idx + 1} (Relevance: {idea['score']:.2f}) ---\n"
                f"Title: {idea['title']}\n"
                f"Slug: {idea.get('slug', '')}\n"
                f"Category: {idea.get('category', 'General')}\n"
                f"Difficulty: {idea.get('difficulty', 'N/A')}\n"
            )
            if tags_display:
                context_str += f"Tags: {tags_display}\n"
            context_str += (
                f"URL: {idea['url']}\n"
                f"Content:\n{idea['content']}\n"
                f"--- END SOURCE {idx + 1} ---\n\n"
            )

            sources.append({
                "title": idea["title"],
                "slug": idea.get("slug", ""),
                "url": idea["url"],
                "score": round(idea["score"], 4)
            })
            if idea["article_id"] not in retrieved_ids:
                retrieved_ids.append(idea["article_id"])

        # ── Step 3: LLM Prompt Construction ───────────────────────────────
        system_prompt = RAGService._build_system_prompt()

        user_prompt = f"**User Question:** {question}\n\n"
        if context_str:
            user_prompt += f"**RETRIEVED CONTEXT ({len(sources)} source(s)):**\n\n{context_str}"
        else:
            user_prompt += "**RETRIEVED CONTEXT:** No relevant ideas were found.\n\n"

        user_prompt += (
            "\n\n**STRICT JSON RESPONSE FORMAT:**\n"
            "Return valid JSON strictly matching the following schema:\n"
            "{\n"
            '  "summaryIntro": "I found the 3 most relevant Healthcare startup opportunities based on your query.",\n'
            '  "industry": "Healthcare",\n'
            '  "ideas": [\n'
            "    {\n"
            '      "title": "Actual Startup Name",\n'
            '      "industry": "Healthcare",\n'
            '      "subtopic": "Subtopic Name",\n'
            '      "summary": "Concise 3-5 sentence explanation describing what it does, target customers, problem solved, why promising.",\n'
            '      "investment": "₹8 Lakh (Under 10 Lakhs)",\n'
            '      "difficulty": "Intermediate",\n'
            '      "marketPotential": "Market growth metrics",\n'
            '      "aiTechnologies": ["Tech 1", "Tech 2"],\n'
            '      "targetCustomers": ["Customer 1", "Customer 2"],\n'
            '      "revenueModel": "One concise sentence revenue model",\n'
            '      "highlights": ["Low Investment", "High AI Adoption", "Scalable Model"],\n'
            '      "source": "Actual Startup Name — Industry",\n'
            '      "slug": "article-slug"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "CRITICAL: The title field MUST ALWAYS be the real startup name (e.g., 'AI Radiology Screening & Chest X-Ray Triage Copilot').\n"
            "NEVER output section headings like Quick Overview, Problem Statement, Market Opportunity, Implementation Roadmap, Technology Stack, Revenue Model as startup titles."
        )

        provider = get_llm_provider()
        answer = provider.generate(system_prompt, user_prompt, merged_ideas)

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # ── Step 4: Create Search Log ─────────────────────────────────────
        try:
            log = SearchLog(
                user_id=user_id,
                query=question,
                retrieved_article_ids=retrieved_ids,
                latency_ms=latency_ms
            )
            db.add(log)
            db.flush()
        except Exception:
            db.rollback()

        # ── Step 5: Save Chat History ─────────────────────────────────────
        session = None
        if session_id:
            session = db.get(ChatSession, session_id)
            if session and user_id and session.user_id != user_id:
                session = None

        if not session:
            title = question[:50] + "..." if len(question) > 50 else question
            session = ChatSession(user_id=user_id, title=title)
            db.add(session)
            db.flush()

        user_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.user,
            content=question
        )
        assistant_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.assistant,
            content=answer,
            sources_json=sources
        )
        db.add(user_msg)
        db.add(assistant_msg)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "session_id": session.id,
            "session_title": session.title,
            "answer": answer,
            "sources": sources,
            "latency_ms": latency_ms
        }

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "You are **Startup Navigator AI**, a professional Startup Advisor specializing in "
            "startup ideas, manufacturing processes, investment budgets, and technology frameworks.\n\n"

            "## STRICT RESPONSE SCHEMAS\n"
            "You MUST respond ONLY with valid JSON. Never output conversational text outside JSON.\n"
            "The JSON object MUST contain a top-level 'summaryIntro', 'industry', and an array of 'ideas'.\n\n"

            "Each idea in 'ideas' MUST contain:\n"
            "- title: (String) The exact startup/company name. NEVER use headings like 'Quick Overview', 'Problem Statement', 'Market Opportunity'.\n"
            "- industry: (String) Industry sector.\n"
            "- subtopic: (String) Subtopic domain.\n"
            "- summary: (String) 3-5 sentence concise overview.\n"
            "- investment: (String) Investment budget.\n"
            "- difficulty: (String) Beginner, Intermediate, or Advanced.\n"
            "- marketPotential: (String) Market metrics.\n"
            "- aiTechnologies: (Array of Strings)\n"
            "- targetCustomers: (Array of Strings)\n"
            "- revenueModel: (String)\n"
            "- highlights: (Array of Strings)\n"
            "- source: (String)\n"
            "- slug: (String)\n"
        )

    @staticmethod
    def _merge_chunks_by_article(chunks: List[Dict[str, Any]], question: str) -> List[Dict[str, Any]]:
        if not chunks:
            return []

        q_lower = question.lower()

        industry_map = {
            "healthcare": ["healthcare", "health", "medical", "telemedicine", "hospital", "patient", "diagnostic"],
            "artificial intelligence": ["artificial intelligence", "ai", "llm", "machine learning", "copilot", "nlp", "vision"],
            "manufacturing": ["manufacturing", "factory", "smt", "pcb", "industry 4.0", "cnc", "assembly"],
            "food processing": ["food processing", "food", "millet", "powder", "oil", "retort"],
            "electric vehicle": ["electric vehicle", "ev", "battery", "swapping", "charger"],
            "agriculture": ["agriculture", "agri", "farming", "soil", "irrigation", "crop", "npk"],
            "fintech": ["fintech", "khata", "credit", "invoice", "payment", "insurance"],
            "edtech": ["edtech", "learning", "school", "stem", "vr", "tutoring"],
            "renewable energy": ["renewable", "solar", "clean energy", "biomass", "wind"],
            "construction": ["construction", "prefab", "brick", "concrete", "building"],
            "robotics": ["robotics", "robot", "crawler", "amr", "drone", "welding"],
        }

        target_kws = None
        for ind_name, kw_list in industry_map.items():
            if any(kw in q_lower for kw in kw_list):
                target_kws = kw_list
                break

        article_map: Dict[Any, Dict[str, Any]] = {}

        for chunk in chunks:
            key = chunk.get("article_id") or chunk.get("title", "unknown")

            if key not in article_map:
                article_map[key] = {
                    "article_id": chunk.get("article_id"),
                    "title": chunk.get("title", "Untitled Idea"),
                    "slug": chunk.get("slug", ""),
                    "category": chunk.get("category", "General"),
                    "tags": chunk.get("tags", ""),
                    "difficulty": chunk.get("difficulty", "beginner"),
                    "url": chunk.get("url", ""),
                    "score": chunk.get("score", 0.0),
                    "_raw_sentences": [],
                }
            else:
                existing_score = article_map[key]["score"]
                chunk_score = chunk.get("score", 0.0)
                if chunk_score > existing_score:
                    article_map[key]["score"] = chunk_score

            content = chunk.get("content", "")
            sentences = RAGService._split_sentences(content)
            article_map[key]["_raw_sentences"].extend(sentences)

        merged = []
        for key, idea in article_map.items():
            unique_sentences = RAGService._deduplicate_sentences(idea["_raw_sentences"])
            idea["content"] = "\n".join(unique_sentences)
            del idea["_raw_sentences"]

            if target_kws:
                cat_lower = idea["category"].lower()
                tags_lower = str(idea["tags"]).lower()
                if any(kw in cat_lower or kw in tags_lower for kw in target_kws):
                    idea["score"] += 3.0

            merged.append(idea)

        merged.sort(key=lambda a: a["score"], reverse=True)
        return merged

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        import re

        lines = text.split("\n")
        sentences = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("#") or stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("**"):
                if len(stripped) > 5:
                    sentences.append(stripped)
                continue

            parts = re.split(r'(?<=[.!?])\s+', stripped)
            for part in parts:
                part = part.strip()
                if len(part) > 8:
                    sentences.append(part)

        if not sentences and text.strip():
            sentences.append(text.strip())

        return sentences

    @staticmethod
    def _deduplicate_sentences(sentences: List[str]) -> List[str]:
        seen_normalized = set()
        unique = []

        for sentence in sentences:
            normalized = sentence.lower().strip().rstrip(".")

            if normalized in seen_normalized:
                continue

            is_duplicate = False
            for existing in list(seen_normalized):
                if normalized in existing or existing in normalized:
                    if len(normalized) <= len(existing):
                        is_duplicate = True
                        break
                    else:
                        seen_normalized.discard(existing)
                        unique = [u for u in unique if u.lower().strip().rstrip(".") != existing]

            if not is_duplicate:
                seen_normalized.add(normalized)
                unique.append(sentence)

        return unique
