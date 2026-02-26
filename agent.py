"""Main agent that orchestrates all memory systems."""

import re
import config
from memory.working import WorkingMemory
from memory.semantic import SemanticMemory
from memory.episodic import EpisodicMemory
from memory.procedural import ProceduralMemory
from memory.consolidation import Consolidation

# Patterns for query classification (compiled once)
_PERSONAL_PATTERNS = re.compile(
    r"we discussed|do you remember|you told me|i told you|i mentioned|"
    r"my budget|my preference|last time|our conversation|remember when",
    re.IGNORECASE,
)
_FACTUAL_PATTERNS = re.compile(
    r"^(what is|what are|how many|how much|tell me about|describe|explain|define)\b",
    re.IGNORECASE,
)
_BEHAVIORAL_PATTERNS = re.compile(
    r"how should i|recommend|best way to|should i|what do you suggest|advice",
    re.IGNORECASE,
)


class CognitiveAgent:
    """Agent with cognitive memory capabilities.

    Args:
        mode: "full" uses all 5 memory systems.
              "semantic_only" uses only working + semantic memory (vanilla RAG baseline).
    """

    def __init__(self, mode: str = "full"):
        self.mode = mode
        self.working = WorkingMemory()
        self.semantic = SemanticMemory()

        if mode == "full":
            self.episodic = EpisodicMemory()
            self.procedural = ProceduralMemory()
            self.consolidation = Consolidation(self.episodic, self.procedural)
        else:
            self.episodic = None
            self.procedural = None
            self.consolidation = None

        self.conversation_count = 0

        # Ingest any documents in data/
        print(f"Loading semantic memory (mode={mode})...")
        self.semantic.ingest_all()

    def _classify_query(self, user_input: str) -> dict:
        """Classify a query to determine which memory systems to activate.

        Returns dict with keys: semantic, episodic, procedural (all bool).
        """
        if _PERSONAL_PATTERNS.search(user_input):
            return {"semantic": False, "episodic": True, "procedural": False}
        if _FACTUAL_PATTERNS.search(user_input):
            return {"semantic": True, "episodic": False, "procedural": False}
        if _BEHAVIORAL_PATTERNS.search(user_input):
            return {"semantic": True, "episodic": True, "procedural": True}
        # Default: activate everything
        return {"semantic": True, "episodic": True, "procedural": True}

    def _detect_conflicts(
        self, semantic_text: str, episodic_text: str, query: str
    ) -> str | None:
        """Check if semantic and episodic contexts contradict each other.

        Makes a short LLM call. Returns a conflict description or None.
        """
        response = self.working.client.messages.create(
            model=config.MODEL_NAME,
            max_tokens=150,
            temperature=0.0,
            system="You detect contradictions between information sources.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Query: {query}\n\n"
                        f"Source A (documents):\n{semantic_text}\n\n"
                        f"Source B (past conversations):\n{episodic_text}\n\n"
                        "Do these two sources contradict each other regarding the query? "
                        "If yes, describe the conflict in one sentence. "
                        "If no, respond with exactly: NONE"
                    ),
                }
            ],
        )
        result = response.content[0].text.strip()
        if result.upper() == "NONE":
            return None
        return result

    def _build_system_prompt(
        self, user_input: str, routing: dict = None
    ) -> str:
        """Construct system prompt with episodic + procedural context.

        Args:
            user_input: The user's query.
            routing: Output of _classify_query. If None, all systems are active.
        """
        base = self.working._default_prompt()
        parts = [base]

        if self.mode != "full":
            return "\n\n".join(parts)

        if routing is None:
            routing = {"semantic": True, "episodic": True, "procedural": True}

        # Episodic context
        if routing["episodic"]:
            episodic_context = self.episodic.recall_as_context(user_input)
            if episodic_context:
                parts.append(
                    "[EPISODIC MEMORY - YOUR PAST EXPERIENCES]\n"
                    "These are YOUR real memories from previous conversations with this user. "
                    "Reference them naturally as your own experience. When the user asks about "
                    "past interactions, use these memories to answer accurately.\n\n"
                    f"{episodic_context}"
                )

        # Procedural rules
        if routing["procedural"]:
            rules = self.procedural.get_rules_text()
            if rules:
                parts.append(
                    "[PROCEDURAL MEMORY - LEARNED RULES]\n"
                    "These rules were learned from your accumulated experience. Follow them.\n\n"
                    f"{rules}"
                )

        return "\n\n".join(parts)

    def chat(self, user_input: str) -> str:
        """Process a user message and return a response."""
        # Classify the query to decide which memory systems to activate
        routing = self._classify_query(user_input) if self.mode == "full" else None

        # Build system prompt with gated memory context
        system_prompt = self._build_system_prompt(user_input, routing=routing)

        # Retrieve semantic context (if gating allows it)
        extra = []
        semantic_text = None
        if routing is None or routing["semantic"]:
            context_msg = self.semantic.recall_as_message(user_input)
            if context_msg:
                extra.append(context_msg)
                semantic_text = context_msg.get("content", "")

        # Conflict detection between semantic and episodic sources
        if (
            config.CONFLICT_DETECTION_ENABLED
            and self.mode == "full"
            and routing
            and routing["semantic"]
            and routing["episodic"]
            and semantic_text
        ):
            episodic_text = self.episodic.recall_as_context(user_input)
            if episodic_text:
                conflict = self._detect_conflicts(
                    semantic_text, episodic_text, user_input
                )
                if conflict:
                    system_prompt += (
                        "\n\n[CONFLICT NOTICE]\n"
                        "The following contradiction was detected between your document "
                        "knowledge and your past conversation memories. Address it "
                        f"transparently in your response.\n\n{conflict}"
                    )

        self.working.update_system_prompt(system_prompt)
        self.working.add_user_message(user_input)

        response = self.working.get_response(extra_messages=extra if extra else None)
        return response

    def new_conversation(self):
        """Start a fresh conversation (preserves long-term memory)."""
        if self.mode == "full" and self.working.get_turn_count() > 0:
            conversation_text = self.working.get_conversation_text()

            # Store episodic memory
            print("  Saving episodic memory...")
            self.episodic.store(conversation_text)

            # Update procedural rules with new learnings
            episodic_context = self.episodic.recall_as_context("recent learnings")
            if episodic_context:
                print("  Updating procedural memory...")
                self.procedural.update(episodic_context)

        self.conversation_count += 1

        # Trigger consolidation every N conversations
        if self.mode == "full" and self.conversation_count % config.CONSOLIDATION_EVERY_N == 0:
            print("  Running memory consolidation (sleep phase)...")
            self.consolidation.run()

        self.working.reset()
