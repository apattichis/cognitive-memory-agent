"""Main agent that orchestrates all memory systems."""

from memory.working import WorkingMemory
from memory.semantic import SemanticMemory
from memory.episodic import EpisodicMemory
from memory.procedural import ProceduralMemory


class CognitiveAgent:
    """Agent with cognitive memory capabilities."""

    def __init__(self):
        self.working = WorkingMemory()
        self.semantic = SemanticMemory()
        self.episodic = EpisodicMemory()
        self.procedural = ProceduralMemory()
        self.conversation_count = 0

        # Ingest any documents in data/
        print("Loading semantic memory...")
        self.semantic.ingest_all()

    def _build_system_prompt(self, user_input: str) -> str:
        """Construct system prompt with episodic + procedural context."""
        base = self.working._default_prompt()
        parts = [base]

        # Episodic context
        episodic_context = self.episodic.recall_as_context(user_input)
        if episodic_context:
            parts.append(
                "You have access to memories from past conversations:\n\n"
                f"{episodic_context}\n\n"
                "Use these past experiences to inform your response when relevant."
            )

        # Procedural rules
        rules = self.procedural.get_rules_text()
        if rules:
            parts.append(
                "Follow these learned behavioral guidelines:\n\n"
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
        if self.working.get_turn_count() > 0:
            conversation_text = self.working.get_conversation_text()

            # Store episodic memory
            print("  Saving episodic memory...")
            self.episodic.store(conversation_text)

            # Update procedural rules with new learnings
            episodic_context = self.episodic.recall_as_context("recent learnings")
            if episodic_context:
                print("  Updating procedural memory...")
                self.procedural.update(episodic_context)

        # Future: trigger consolidation every N conversations
        self.conversation_count += 1
        self.working.reset()
