"""Working memory - maintains current conversation state."""

from anthropic import Anthropic
import config


class WorkingMemory:
    """Chat history buffer that holds the current conversation context."""

    def __init__(self, system_prompt: str = None):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.system_prompt = system_prompt or self._default_prompt()
        self.messages: list[dict] = []

    def _default_prompt(self) -> str:
        return (
            "You are an assistant with persistent memory across conversations. "
            "You have three memory systems: episodic (past conversation experiences), "
            "semantic (factual knowledge from documents), and procedural (learned behavioral rules). "
            "When memory context is provided, treat it as ground truth from your own experience. "
            "Prioritize retrieved knowledge over your general training when they conflict. "
            "Be direct and concise. Never claim you lack memory if memories are provided below."
        )

    def update_system_prompt(self, new_prompt: str):
        """Replace the system prompt (used when injecting memory context)."""
        self.system_prompt = new_prompt

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def get_response(self, extra_messages: list[dict] = None) -> str:
        """Send messages to LLM and get a response.

        Args:
            extra_messages: Optional messages to append before the LLM call
                (e.g., semantic context) without persisting them in history.
        """
        messages = self.messages.copy()
        if extra_messages:
            # Insert context messages before the last user message
            last_user = messages.pop()
            messages.extend(extra_messages)
            messages.append(last_user)

        response = self.client.messages.create(
            model=config.MODEL_NAME,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            system=self.system_prompt,
            messages=messages,
        )
        reply = response.content[0].text
        self.add_assistant_message(reply)
        return reply

    def get_conversation_text(self) -> str:
        """Return full conversation as plain text (for episodic storage)."""
        lines = []
        for msg in self.messages:
            role = msg["role"].capitalize()
            lines.append(f"{role}: {msg['content']}")
        return "\n\n".join(lines)

    def get_turn_count(self) -> int:
        """Number of user messages in this conversation."""
        return sum(1 for m in self.messages if m["role"] == "user")

    def reset(self):
        """Clear conversation history, keep system prompt."""
        self.messages = []
