"""Full end-to-end demo exercising all 5 memory systems.

Run with:
    conda activate cognitive-memory
    export ANTHROPIC_API_KEY="your-key"
    cd ~/VSCode/Projects/cognitive-memory-agent
    python test_full_demo.py
"""

import json
import os
import shutil

from agent import CognitiveAgent


def divider(step, title):
    print(f"\n{'='*60}")
    print(f"STEP {step}: {title}")
    print(f"{'='*60}\n")


def main():
    # Clean slate
    if os.path.exists("chroma_db"):
        shutil.rmtree("chroma_db")
    if os.path.exists("procedural_memory.txt"):
        os.remove("procedural_memory.txt")

    agent = CognitiveAgent()

    # --- STEP 1: Semantic Memory ---
    divider(1, "SEMANTIC MEMORY - Query the fake PDF")
    r = agent.chat("What is the Zeltron stock ticker and what programming language do they use?")
    print(f"Agent: {r}")
    print(f"\n[Semantic chunks in DB: {agent.semantic.collection.count()}]")

    # --- STEP 2: Save episodic + procedural ---
    divider(2, "SAVE EPISODIC + PROCEDURAL from Conv 1")
    agent.new_conversation()
    print(f"[Episodic memories stored: {agent.episodic.collection.count()}]")
    print(f"[Procedural rules: {len(agent.procedural.rules)}]")
    for i, rule in enumerate(agent.procedural.rules):
        print(f"  Rule {i+1}: {rule}")

    # --- STEP 3: Episodic recall ---
    divider(3, "EPISODIC RECALL - New conversation, ask about past")
    r = agent.chat("What did we talk about in our previous conversation?")
    print(f"Agent: {r}")

    # --- STEP 4: Build more episodic memories ---
    divider(4, "BUILD MORE EPISODES (Conv 2-5)")

    agent.new_conversation()
    agent.chat("How many resonators does the QA-7 have?")
    agent.new_conversation()
    print(f"  Conv 2 done. Episodes: {agent.episodic.collection.count()}")

    agent.chat("Tell me about Zeltron employee ranks")
    agent.new_conversation()
    print(f"  Conv 3 done. Episodes: {agent.episodic.collection.count()}")

    agent.chat("Who are Zeltron competitors?")
    agent.new_conversation()
    print(f"  Conv 4 done. Episodes: {agent.episodic.collection.count()}")

    agent.chat("What is the Solvik Temperature?")

    # --- STEP 5: Consolidation ---
    divider(5, "CONSOLIDATION - Conv 5 triggers sleep phase")
    agent.new_conversation()  # This is conversation #5, triggers consolidation
    print(f"[Episodes after consolidation: {agent.episodic.collection.count()}]")
    print(f"[Procedural rules after consolidation: {len(agent.procedural.rules)}]")
    for i, rule in enumerate(agent.procedural.rules):
        print(f"  Rule {i+1}: {rule}")

    # --- STEP 6: All systems in one query ---
    divider(6, "FINAL TEST - All systems active in one query")
    r = agent.chat("Based on everything we have discussed, give me a summary of Zeltron Corporation.")
    print(f"Agent: {r}")

    # --- Final state ---
    divider("DONE", "FINAL STATE")
    print(f"Semantic chunks:    {agent.semantic.collection.count()}")
    print(f"Episodic memories:  {agent.episodic.collection.count()}")
    print(f"Procedural rules:   {len(agent.procedural.rules)}")
    print(f"Conversations held: {agent.conversation_count}")
    print(f"Procedural file:    {os.path.exists('procedural_memory.txt')}")

    if os.path.exists("procedural_memory.txt"):
        with open("procedural_memory.txt") as f:
            rules = json.load(f)
        print(f"\nPersisted rules ({len(rules)}):")
        for i, rule in enumerate(rules):
            print(f"  {i+1}. {rule}")


if __name__ == "__main__":
    main()
