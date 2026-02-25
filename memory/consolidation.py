"""Memory consolidation - periodic sleep phase that merges, compresses, and promotes."""

import json
import numpy as np
from anthropic import Anthropic
import config
from memory.episodic import EpisodicMemory
from memory.procedural import ProceduralMemory


MERGE_PROMPT = """You are a memory consolidation system. Multiple episodic memories cover overlapping topics. Merge them into ONE unified memory that preserves all unique information.

<episodes>
{episodes}
</episodes>

Rules:
- Preserve every distinct fact, lesson, or insight from the originals
- Remove only exact duplicates, not similar-but-different points
- The merged summary should cover the full scope of all episodes
- Combine "what worked" and "what to avoid" lists additively

Return ONLY valid JSON with these fields (no markdown, no code fences):
- "summary": one sentence covering the merged topic
- "what_worked": combined effective approaches from all episodes
- "what_to_avoid": combined pitfalls from all episodes
- "context_tags": 2-4 keywords covering all merged topics"""


PROMOTION_PROMPT = """You are a pattern extraction system. Analyze these episodic memories and identify recurring behavioral patterns that should become permanent rules.

<memories>
{episodes}
</memories>

Criteria for promotion:
- A pattern must appear in at least 2 separate memories to qualify
- Rules must be specific and actionable, not vague generalizations
- Only extract patterns clearly supported by evidence in the memories

Return ONLY a JSON array of rule strings. If no patterns meet the criteria, return [].
No explanation, no markdown."""


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return dot / norm if norm > 0 else 0.0


def cluster_episodes(episodes: list[dict], threshold: float) -> list[list[dict]]:
    """Group episodes by embedding similarity using simple greedy clustering."""
    if not episodes or not episodes[0].get("embedding"):
        return [[ep] for ep in episodes]

    used = set()
    clusters = []

    for i, ep_a in enumerate(episodes):
        if i in used:
            continue
        cluster = [ep_a]
        used.add(i)

        for j, ep_b in enumerate(episodes):
            if j in used:
                continue
            sim = cosine_similarity(ep_a["embedding"], ep_b["embedding"])
            if sim >= threshold:
                cluster.append(ep_b)
                used.add(j)

        clusters.append(cluster)

    return clusters


class Consolidation:
    """Periodic memory consolidation - merge similar episodes and promote patterns."""

    def __init__(self, episodic: EpisodicMemory, procedural: ProceduralMemory):
        self.episodic = episodic
        self.procedural = procedural
        self.llm = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def run(self):
        """Execute a full consolidation cycle."""
        episodes = self.episodic.get_all()
        if len(episodes) < 2:
            print("  Not enough episodes to consolidate.")
            return

        print(f"  Consolidating {len(episodes)} episodes...")

        # Step 1: Cluster similar episodes
        clusters = cluster_episodes(episodes, config.CONSOLIDATION_THRESHOLD)
        mergeable = [c for c in clusters if len(c) >= 2]

        # Step 2: Merge clusters
        merged_count = 0
        for cluster in mergeable:
            success = self._merge_cluster(cluster)
            if success:
                merged_count += 1

        if merged_count:
            print(f"  Merged {merged_count} clusters.")

        # Step 3: Promote recurring patterns to procedural memory
        self._promote_patterns()

    def _merge_cluster(self, cluster: list[dict]) -> bool:
        """Merge a cluster of similar episodes into one."""
        episode_texts = []
        for ep in cluster:
            meta = ep["metadata"]
            episode_texts.append(
                f"Summary: {meta.get('summary', 'N/A')}\n"
                f"What worked: {meta.get('what_worked', 'N/A')}\n"
                f"What to avoid: {meta.get('what_to_avoid', 'N/A')}"
            )

        try:
            response = self.llm.messages.create(
                model=config.MODEL_NAME,
                max_tokens=512,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": MERGE_PROMPT.format(
                        episodes="\n\n---\n\n".join(episode_texts)
                    ),
                }],
            )
            text = response.content[0].text
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            merged = json.loads(text.strip())
        except (json.JSONDecodeError, IndexError, KeyError):
            return False

        # Delete originals
        ids_to_delete = [ep["id"] for ep in cluster]
        self.episodic.delete(ids_to_delete)

        # Store merged episode
        import time
        merged_doc = (
            f"Summary: {merged['summary']}\n"
            f"What worked: {merged['what_worked']}\n"
            f"What to avoid: {merged['what_to_avoid']}\n\n"
            f"[Consolidated from {len(cluster)} episodes]"
        )
        self.episodic.collection.add(
            ids=[f"consolidated_{int(time.time() * 1000)}"],
            documents=[merged_doc],
            metadatas=[{
                "timestamp": time.time(),
                "summary": merged["summary"],
                "what_worked": merged["what_worked"],
                "what_to_avoid": merged["what_to_avoid"],
                "context_tags": ",".join(merged.get("context_tags", [])),
                "consolidated": "true",
            }],
        )
        return True

    def _promote_patterns(self):
        """Extract recurring patterns from episodes and promote to procedural memory."""
        episodes = self.episodic.get_all()
        if len(episodes) < config.PROMOTION_MIN_OCCURRENCES:
            return

        episode_texts = []
        for ep in episodes:
            meta = ep["metadata"]
            episode_texts.append(
                f"Summary: {meta.get('summary', 'N/A')}\n"
                f"What worked: {meta.get('what_worked', 'N/A')}\n"
                f"What to avoid: {meta.get('what_to_avoid', 'N/A')}"
            )

        try:
            response = self.llm.messages.create(
                model=config.MODEL_NAME,
                max_tokens=512,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": PROMOTION_PROMPT.format(
                        episodes="\n\n---\n\n".join(episode_texts)
                    ),
                }],
            )
            text = response.content[0].text
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            rules = json.loads(text.strip())
        except (json.JSONDecodeError, IndexError, KeyError):
            return

        if isinstance(rules, list):
            promoted = 0
            for rule in rules:
                if isinstance(rule, str) and rule.strip():
                    self.procedural.add_rule(rule.strip())
                    promoted += 1
            if promoted:
                print(f"  Promoted {promoted} patterns to procedural memory.")
