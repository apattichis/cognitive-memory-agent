"""Procedural memory - self-updating behavioral rules learned from experience."""

import json
import os
from anthropic import Anthropic
import config


UPDATE_PROMPT = """You maintain a set of behavioral guidelines for an AI assistant.
You are given the current rules and new learnings from recent conversations.

Current rules:
{current_rules}

New learnings from recent conversations:
{new_learnings}

Update the rules by:
1. Keep rules that are still valid
2. Merge new learnings into existing rules where they overlap
3. Add genuinely new rules from the learnings
4. Remove rules that are contradicted by new evidence
5. Cap at {max_rules} rules total, prioritize by importance

Return ONLY a JSON array of strings, each being one rule. Example:
["Rule 1 text", "Rule 2 text", "Rule 3 text"]"""


class ProceduralMemory:
    """Self-updating behavioral rules that evolve with experience."""

    def __init__(self):
        self.llm = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.rules: list[str] = self._load()

    def _load(self) -> list[str]:
        """Load rules from file."""
        if not os.path.exists(config.PROCEDURAL_MEMORY_FILE):
            return []
        try:
            with open(config.PROCEDURAL_MEMORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save(self):
        """Persist rules to file."""
        with open(config.PROCEDURAL_MEMORY_FILE, "w") as f:
            json.dump(self.rules, f, indent=2)

    def get_rules_text(self) -> str | None:
        """Format rules for system prompt injection."""
        if not self.rules:
            return None
        lines = [f"{i+1}. {rule}" for i, rule in enumerate(self.rules)]
        return "\n".join(lines)

    def update(self, new_learnings: str):
        """Incrementally update rules based on new learnings."""
        if not new_learnings.strip():
            return

        current = self.get_rules_text() or "No rules yet."

        try:
            response = self.llm.messages.create(
                model=config.MODEL_NAME,
                max_tokens=1024,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": UPDATE_PROMPT.format(
                        current_rules=current,
                        new_learnings=new_learnings,
                        max_rules=config.MAX_PROCEDURAL_RULES,
                    ),
                }],
            )
            text = response.content[0].text
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            updated = json.loads(text.strip())
            if isinstance(updated, list) and all(isinstance(r, str) for r in updated):
                self.rules = updated[:config.MAX_PROCEDURAL_RULES]
                self._save()
        except (json.JSONDecodeError, IndexError, KeyError):
            pass  # keep existing rules if update fails

    def add_rule(self, rule: str):
        """Directly add a rule (used by consolidation promotion)."""
        if rule not in self.rules:
            self.rules.append(rule)
            if len(self.rules) > config.MAX_PROCEDURAL_RULES:
                self.rules = self.rules[-config.MAX_PROCEDURAL_RULES:]
            self._save()
