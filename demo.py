"""CLI chat interface for the cognitive memory agent."""

from agent import CognitiveAgent


def main():
    agent = CognitiveAgent()

    print("Cognitive Memory Agent")
    print("Commands: /new (new conversation), /quit (exit)")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            break

        if user_input.lower() == "/new":
            agent.new_conversation()
            print("\n--- New conversation started ---")
            continue

        response = agent.chat(user_input)
        print(f"\nAgent: {response}")

    print("\nGoodbye.")


if __name__ == "__main__":
    main()
