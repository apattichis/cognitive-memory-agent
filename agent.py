"""Main agent that orchestrates all memory systems."""

import config
from memory.working import WorkingMemory
from memory.semantic import SemanticMemory
from memory.episodic import EpisodicMemory
from memory.procedural import ProceduralMemory
from memory.consolidation import Consolidation


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

    def _build_system_prompt(self, user_input: str) -> str:
        """Construct system prompt with episodic + procedural context."""
        base = self.working._default_prompt()
        parts = [base]

        if self.mode != "full":
            return "\n\n".join(parts)

        # Episodic context
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
        # Build system prompt with all memory context
        system_prompt = self._build_system_prompt(user_input)
        self.working.update_system_prompt(system_prompt)

        self.working.add_user_message(user_input)

        # Retrieve semantic context
        extra = []
        context_msg = self.semantic.recall_as_message(user_input)
        if context_msg:
            extra.append(context_msg)

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
