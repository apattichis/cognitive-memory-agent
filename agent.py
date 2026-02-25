"""Main agent that orchestrates all memory systems."""

from memory.working import WorkingMemory
from memory.semantic import SemanticMemory


class CognitiveAgent:
    """Agent with cognitive memory capabilities."""

    def __init__(self):
        self.working = WorkingMemory()
        self.semantic = SemanticMemory()
        self.conversation_count = 0

        # Ingest any documents in data/
        print("Loading semantic memory...")
        self.semantic.ingest_all()

    def chat(self, user_input: str) -> str:
        """Process a user message and return a response."""
        self.working.add_user_message(user_input)

        # Retrieve semantic context
        extra = []
        context_msg = self.semantic.recall_as_message(user_input)
        if context_msg:
            extra.append(context_msg)

        # Future: retrieve episodic context
        # Future: inject procedural rules into system prompt

        response = self.working.get_response(extra_messages=extra if extra else None)
        return response

    def new_conversation(self):
        """Start a fresh conversation (preserves long-term memory)."""
        # Future: store episodic memory before resetting
        # Future: trigger consolidation every N conversations
        self.conversation_count += 1
        self.working.reset()
