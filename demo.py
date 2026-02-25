"""CLI chat interface for the cognitive memory agent."""

from agent import CognitiveAgent


def main():
    agent = CognitiveAgent()

    print("Cognitive Memory Agent")
    print("Commands: /new (new conversation), /ingest (reload docs), /sleep (consolidate), /quit (exit)")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            # Save current conversation before exiting
            agent.new_conversation()
            break

        if user_input.lower() == "/new":
            agent.new_conversation()
            print("\n--- New conversation started ---")
            continue

        if user_input.lower() == "/ingest":
            agent.semantic.ingest_all()
            print("\n--- Documents reloaded ---")
            continue

        if user_input.lower() == "/sleep":
            print("\n--- Running memory consolidation ---")
            agent.consolidation.run()
            print("--- Consolidation complete ---")
            continue

        response = agent.chat(user_input)
        print(f"\nAgent: {response}")

    print("\nGoodbye.")


if __name__ == "__main__":
    main()
