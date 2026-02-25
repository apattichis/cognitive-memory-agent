"""Episodic memory - stores past conversations with LLM-generated reflections."""

import json
import math
import time
import chromadb
from anthropic import Anthropic
import config


REFLECTION_PROMPT_TEMPLATE = """You are a memory encoder. Your task is to extract a structured reflection from a conversation so it can be stored and retrieved later.

<conversation>
{conversation}
</conversation>

Extract the following fields and return ONLY valid JSON (no markdown, no code fences):
- "context_tags": 2-4 specific keywords for retrieval (e.g. "QA-7", "processor", "Zeltron" not generic words like "technology")
- "summary": one factual sentence capturing the key topic and outcome
- "what_worked": specific approaches that were effective, or "N/A" if none
- "what_to_avoid": specific mistakes or pitfalls identified, or "N/A" if none"""


class EpisodicMemory:
    """Stores past conversation experiences with reflections for future recall."""

    def __init__(self):
        db = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        self.collection = db.get_or_create_collection(
            name="episodic_memory",
            metadata={"hnsw:space": "cosine"},
        )
        self.llm = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def store(self, conversation_text: str):
        """Reflect on a conversation and store it as an episodic memory."""
        if not conversation_text.strip():
            return

        reflection = self._reflect(conversation_text)
        if not reflection:
            return

        episode_id = f"episode_{int(time.time() * 1000)}"
        document = (
            f"Summary: {reflection['summary']}\n"
            f"What worked: {reflection['what_worked']}\n"
            f"What to avoid: {reflection['what_to_avoid']}\n\n"
            f"Full conversation:\n{conversation_text}"
        )

        self.collection.add(
            ids=[episode_id],
            documents=[document],
            metadatas=[{
                "timestamp": time.time(),
                "summary": reflection["summary"],
                "what_worked": reflection["what_worked"],
                "what_to_avoid": reflection["what_to_avoid"],
                "context_tags": ",".join(reflection["context_tags"]),
            }],
        )

    def recall(self, query: str) -> list[dict] | None:
        """Retrieve relevant past episodes with recency weighting."""
        if self.collection.count() == 0:
            return None

        n = min(config.EPISODIC_TOP_K * 2, self.collection.count())
        results = self.collection.query(
            query_texts=[query],
            n_results=n,
        )

        if not results["documents"][0]:
            return None

        # Apply recency weighting and re-rank
        scored = []
        now = time.time()
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity = 1 - distance  # cosine distance -> similarity

            age_hours = (now - meta["timestamp"]) / 3600
            recency = math.exp(-0.693 * age_hours / config.RECENCY_HALF_LIFE_HOURS)

            score = similarity * 0.7 + recency * 0.3
            scored.append({"score": score, "metadata": meta, "document": doc})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:config.EPISODIC_TOP_K]

    def recall_as_context(self, query: str) -> str | None:
        """Format recalled episodes as text for system prompt injection."""
        episodes = self.recall(query)
        if not episodes:
            return None

        parts = []
        for i, ep in enumerate(episodes):
            meta = ep["metadata"]
            parts.append(
                f"[Past experience {i+1}]\n"
                f"Summary: {meta['summary']}\n"
                f"What worked: {meta['what_worked']}\n"
                f"What to avoid: {meta['what_to_avoid']}"
            )
        return "\n\n".join(parts)

    def get_all(self) -> list[dict]:
        """Return all stored episodes (used by consolidation)."""
        if self.collection.count() == 0:
            return []

        results = self.collection.get(include=["documents", "metadatas", "embeddings"])
        episodes = []
        for i, doc in enumerate(results["documents"]):
            episodes.append({
                "id": results["ids"][i],
                "document": doc,
                "metadata": results["metadatas"][i],
                "embedding": results["embeddings"][i] if results["embeddings"] is not None else None,
            })
        return episodes

    def delete(self, ids: list[str]):
        """Delete episodes by ID (used by consolidation)."""
        if ids:
            self.collection.delete(ids=ids)

    def _reflect(self, conversation_text: str) -> dict | None:
        """Use LLM to generate structured reflection on a conversation."""
        try:
            response = self.llm.messages.create(
                model=config.MODEL_NAME,
                max_tokens=512,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": REFLECTION_PROMPT_TEMPLATE.format(conversation=conversation_text),
                }],
            )
            text = response.content[0].text
            # Extract JSON from response (handle markdown code blocks)
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except (json.JSONDecodeError, IndexError, KeyError):
            return None
