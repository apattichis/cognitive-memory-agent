"""Main agent that orchestrates all memory systems."""

from memory.working import WorkingMemory
from memory.semantic import SemanticMemory
from memory.episodic import EpisodicMemory


class CognitiveAgent:
    """Agent with cognitive memory capabilities."""

    def __init__(self):
        self.working = WorkingMemory()
        self.semantic = SemanticMemory()
        self.episodic = EpisodicMemory()
        self.conversation_count = 0

        # Ingest any documents in data/
        print("Loading semantic memory...")
        self.semantic.ingest_all()

    def chat(self, user_input: str) -> str:
        """Process a user message and return a response."""
        # Inject episodic context into system prompt before responding
        episodic_context = self.episodic.recall_as_context(user_input)
        if episodic_context:
            base = self.working._default_prompt()
            self.working.update_system_prompt(
                f"{base}\n\n"
                f"You have access to memories from past conversations:\n\n"
                f"{episodic_context}\n\n"
                f"Use these past experiences to inform your response when relevant."
            )

        self.working.add_user_message(user_input)

        # Retrieve semantic context
        extra = []
        context_msg = self.semantic.recall_as_message(user_input)
        if context_msg:
            extra.append(context_msg)

        # Future: inject procedural rules into system prompt

        response = self.working.get_response(extra_messages=extra if extra else None)
        return response

    def new_conversation(self):
        """Start a fresh conversation (preserves long-term memory)."""
        # Store episodic memory before resetting
        if self.working.get_turn_count() > 0:
            conversation_text = self.working.get_conversation_text()
            print("  Saving episodic memory...")
            self.episodic.store(conversation_text)

        # Future: trigger consolidation every N conversations
        self.conversation_count += 1
        self.working.reset()
