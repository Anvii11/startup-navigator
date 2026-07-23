import os
import re
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

FORBIDDEN_HEADINGS = {
    "quick overview", "problem statement", "market opportunity", "implementation roadmap",
    "technology stack", "revenue model", "executive summary", "key highlights",
    "target customers", "references", "government schemes", "financial plan"
}


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, context_documents: List[Dict[str, Any]]) -> str:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str, context_documents: List[Dict[str, Any]]) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model_name = "gemini-1.5-flash"

    def generate(self, system_prompt: str, user_prompt: str, context_documents: List[Dict[str, Any]]) -> str:
        import google.generativeai as genai
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )
        response = model.generate_content(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        return response.text


class MockProvider(LLMProvider):
    """
    Synthesizes grounded, recruiter-quality structured JSON responses from retrieved context documents.
    Prevents section heading leaks into title and outputs exact requested schema.
    """

    INDUSTRY_KEYWORDS = {
        "healthcare": ["healthcare", "health", "medical", "telemedicine", "hospital", "doctor", "diagnostic", "patient"],
        "artificial-intelligence": ["artificial intelligence", "ai", "llm", "machine learning", "copilot", "nlp", "vision"],
        "manufacturing-industry-4-0": ["manufacturing", "factory", "smt", "pcb", "industry 4.0", "cnc", "assembly"],
        "food-processing": ["food processing", "food", "millet", "powder", "oil", "retort", "dehydrated"],
        "electric-vehicles": ["electric vehicle", "ev", "battery", "swapping", "charger", "charging"],
        "agriculture": ["agriculture", "agri", "farming", "soil", "irrigation", "crop", "npk", "drone"],
        "fintech": ["fintech", "khata", "credit", "invoice", "payment", "insurance", "upi"],
        "edtech": ["edtech", "learning", "school", "stem", "vr", "tutoring", "education"],
        "renewable-energy": ["renewable", "solar", "clean energy", "biomass", "wind", "briquette"],
        "construction-tech": ["construction", "prefab", "brick", "concrete", "building", "interlocking"],
        "robotics": ["robotics", "robot", "crawler", "amr", "drone", "welding", "automation"],
    }

    def generate(self, system_prompt: str, user_prompt: str, context_documents: List[Dict[str, Any]]) -> str:
        if not context_documents:
            return self._no_context_response(user_prompt)

        question = self._extract_question(user_prompt)
        question_lower = question.lower()

        # Group context chunks by article
        idea_map: Dict[Any, Dict[str, Any]] = {}
        for doc in context_documents:
            key = doc.get("article_id") or doc.get("title", "unknown")
            if key not in idea_map:
                idea_map[key] = {
                    "article_id": doc.get("article_id"),
                    "title": doc.get("title", "Untitled Idea"),
                    "slug": doc.get("slug", ""),
                    "category": doc.get("category", "General"),
                    "tags": doc.get("tags", ""),
                    "difficulty": doc.get("difficulty", "intermediate"),
                    "score": doc.get("score", 0.0),
                    "content_parts": [],
                }
            else:
                if doc.get("score", 0.0) > idea_map[key]["score"]:
                    idea_map[key]["score"] = doc.get("score", 0.0)
            idea_map[key]["content_parts"].append(doc.get("content", ""))

        all_ideas = list(idea_map.values())

        # Determine target industry filter if present in query
        target_industry = None
        for ind_slug, kw_list in self.INDUSTRY_KEYWORDS.items():
            if any(kw in question_lower for kw in kw_list):
                target_industry = ind_slug
                break

        # Domain relevance filtering
        if target_industry:
            matched_ideas = []
            for idea in all_ideas:
                cat_lower = idea["category"].lower()
                tags_lower = str(idea["tags"]).lower()
                kw_list = self.INDUSTRY_KEYWORDS[target_industry]
                if any(kw in cat_lower or kw in tags_lower for kw in kw_list):
                    matched_ideas.append(idea)
            
            if matched_ideas:
                all_ideas = matched_ideas

        all_ideas.sort(key=lambda x: x["score"], reverse=True)
        selected_ideas = all_ideas[:3]

        if not selected_ideas:
            return self._no_context_response(user_prompt)

        return self._format_advisor_json_response(question, selected_ideas)

    def _format_advisor_json_response(self, question: str, ideas: List[Dict[str, Any]]) -> str:
        ind_name = ideas[0]["category"] if ideas else "Startup & Manufacturing"
        count = len(ideas)

        ideas_list = []
        for idea in ideas:
            full_content = "\n".join(idea["content_parts"])
            parsed = self._parse_idea_details(full_content, idea)

            ideas_list.append({
                "title": parsed["title"],
                "industry": parsed["industry"],
                "subtopic": parsed["subtopic"],
                "summary": parsed["summary"],
                "investment": parsed["investment"],
                "difficulty": parsed["difficulty"].capitalize(),
                "marketPotential": parsed["market_opportunity"],
                "aiTechnologies": parsed["ai_tech_list"],
                "targetCustomers": parsed["target_customers_list"],
                "revenueModel": parsed["revenue_model"],
                "highlights": [
                    f"Low Investment ({parsed['investment']})",
                    "High AI Adoption",
                    "Scalable B2B Model",
                    f"Growing Market ({parsed['market_opportunity']})",
                    "Government Support"
                ],
                "source": f'{parsed["title"]} — {parsed["industry"]}',
                "slug": idea.get("slug", "")
            })

        payload = {
          "summaryIntro": f"I found the {count} most relevant {ind_name} startup opportunities based on your query.",
          "industry": ind_name,
          "ideas": ideas_list
        }

        return json.dumps(payload, indent=2)

    def _parse_idea_details(self, content: str, idea_meta: Dict[str, Any]) -> Dict[str, Any]:
        # Validate title strictly against DB record to prevent heading leaks
        raw_title = idea_meta.get("title", "Untitled Startup Idea")
        if not raw_title or raw_title.strip().lower() in FORBIDDEN_HEADINGS:
            title = "High Potential Startup Idea"
        else:
            title = raw_title.strip()

        industry = idea_meta.get("category", "General")
        difficulty = idea_meta.get("difficulty", "intermediate")
        tags_str = str(idea_meta.get("tags", ""))

        # Subtopic
        subtopic = "General"
        sub_match = re.search(r"\*\*Subtopic:\*\*\s*(.+)", content, re.IGNORECASE)
        if sub_match:
            subtopic = sub_match.group(1).strip()
        else:
            tags_list = tags_str.split(",") if isinstance(tags_str, str) else []
            for t in tags_list:
                t_clean = t.strip()
                if t_clean and not t_clean.startswith("investment-") and not t_clean.startswith("ai-") and t_clean != industry.lower():
                    subtopic = t_clean.title()
                    break

        # Investment
        investment = "Under ₹10 Lakh"
        inv_match = re.search(r"\*\*Estimated Investment:\*\*\s*(.+)", content, re.IGNORECASE)
        if inv_match:
            investment = inv_match.group(1).strip()

        # Problem & Solution for Summary
        problem = self._extract_section(content, "Problem Statement")
        solution = self._extract_section(content, "Solution")
        if not solution:
            solution = self._extract_section(content, "Executive Summary") or idea_meta.get("summary", "")

        target_cust_raw = self._extract_section(content, "Target Customers") or "Mid-market enterprises, regional SMBs, retail buyers"
        target_cust_clean = re.sub(r"#+|\*\*|__", "", target_cust_raw).strip()
        target_customers_list = [c.strip() for c in target_cust_clean.split(",") if c.strip()]

        clean_sol = re.sub(r"#+|\*\*|__", "", solution).strip()
        clean_prob = re.sub(r"#+|\*\*|__", "", problem).strip()
        
        overview_sentences = []
        if clean_sol:
            overview_sentences.append(clean_sol)
        if clean_prob:
            overview_sentences.append(f"This directly addresses a challenge where {clean_prob.lower()[:150]}.")
        if target_cust_clean:
            overview_sentences.append(f"The platform serves {target_cust_clean.lower()[:120]}.")
        overview_sentences.append("It provides a scalable, high-margin venture eligible for government schemes.")

        summary = " ".join(overview_sentences[:4])

        market_opportunity = self._extract_section(content, "Market Opportunity") or "High growth market expanding at 15%+ CAGR."
        market_opportunity = re.sub(r"#+|\*\*|__", "", market_opportunity).strip()

        ai_tech_raw = self._extract_section(content, "AI & Automation Opportunities") or self._extract_section(content, "Technology Stack") or "Generative AI, machine learning automation, cloud APIs"
        ai_tech_clean = re.sub(r"#+|\*\*|__", "", ai_tech_raw).strip()
        ai_tech_list = [t.strip() for t in re.split(r"[,;•\n]", ai_tech_clean) if t.strip() and len(t.strip()) > 2][:4]

        revenue_model = self._extract_section(content, "Revenue Model") or "SaaS B2B monthly subscription and hardware unit margin."
        revenue_model = re.sub(r"#+|\*\*|__", "", revenue_model).strip()

        return {
            "title": title,
            "industry": industry,
            "subtopic": subtopic,
            "summary": summary,
            "target_customers_list": target_customers_list,
            "investment": investment,
            "market_opportunity": market_opportunity,
            "ai_tech_list": ai_tech_list,
            "revenue_model": revenue_model,
            "difficulty": difficulty,
        }

    @staticmethod
    def _extract_section(content: str, section_title: str) -> str:
        pattern = r"##\s*" + re.escape(section_title) + r"\n+([^\n#]+(?:\n[^\n#]+)*)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _no_context_response(self, user_prompt: str) -> str:
        return json.dumps({
          "summaryIntro": "I found relevant startup recommendations from our knowledge base for your query.",
          "industry": "Manufacturing & Industry 4.0",
          "ideas": [
            {
              "title": "Micro-Factory SMT Electronics PCB Assembly Line",
              "industry": "Manufacturing & Industry 4.0",
              "subtopic": "PCB Assembly",
              "summary": "A micro-factory setup equipped with desktop Pick-and-Place machines for quick-turn prototype assembly. Hardware startups struggle with high MOQ penalties for small PCB assembly runs. Serves IoT startups, robotics developers, EV makers.",
              "investment": "₹8 Lakh (Under 10 Lakhs)",
              "difficulty": "Intermediate",
              "marketPotential": "$100B EMS market",
              "aiTechnologies": ["Computer vision inspection", "OpenPNP PnP machine", "Reflow Oven"],
              "targetCustomers": ["IoT startups", "Robotics developers", "EV makers"],
              "revenueModel": "Turnkey assembly fees per board (₹150 to ₹800/board)",
              "highlights": ["Low Investment", "High AI Adoption", "Scalable Model", "Government Support"],
              "source": "Micro-Factory SMT Electronics PCB Assembly Line — Manufacturing & Industry 4.0",
              "slug": "micro-factory-smt-electronics-pcb-assembly-line"
            }
          ]
        }, indent=2)

    @staticmethod
    def _extract_question(user_prompt: str) -> str:
        for line in user_prompt.split("\n"):
            if "User Question:" in line:
                return line.split("User Question:", 1)[1].strip().strip("*")
        for line in user_prompt.split("\n"):
            stripped = line.strip()
            if stripped:
                return stripped
        return user_prompt


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider_type = (os.getenv("LLM_PROVIDER") or settings.app_env).lower()

    openai_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
    gemini_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "gemini_api_key", None)

    if provider_type == "openai" or (not provider_type and openai_key):
        if openai_key:
            try:
                return OpenAIProvider(api_key=openai_key)
            except Exception:
                pass
        return MockProvider()

    elif provider_type == "gemini":
        if gemini_key:
            try:
                return GeminiProvider(api_key=gemini_key)
            except Exception:
                pass
        return MockProvider()

    return MockProvider()
