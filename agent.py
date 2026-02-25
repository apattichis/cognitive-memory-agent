"""Main agent that orchestrates all memory systems."""

from memory.working import WorkingMemory


class CognitiveAgent:
    """Agent with cognitive memory capabilities.

    Currently uses working memory only. Episodic, semantic, and procedural
    memory will be added in subsequent stages.
    """

    def __init__(self):
        self.working = WorkingMemory()
        self.conversation_count = 0

    def chat(self, user_input: str) -> str:
        """Process a user message and return a response."""
        self.working.add_user_message(user_input)

        # Future: retrieve episodic context
        # Future: retrieve semantic context
        # Future: inject procedural rules into system prompt

        response = self.working.get_response()
        return response

    def new_conversation(self):
        """Start a fresh conversation (preserves long-term memory)."""
        # Future: store episodic memory before resetting
        # Future: trigger consolidation every N conversations
        self.conversation_count += 1
        self.working.reset()
