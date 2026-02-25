# Cognitive Memory Agent

A Python chatbot with four memory systems inspired by cognitive architectures:

- **Working Memory** - Current conversation context
- **Semantic Memory** - RAG over documents (ChromaDB)
- **Episodic Memory** - Past conversation storage with reflections
- **Procedural Memory** - Self-updating behavioral rules
- **Consolidation** - Periodic memory merging, compression, and knowledge promotion

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python demo.py
```

## Usage

```
You: What is retrieval augmented generation?
Agent: ...

/new    - Start a new conversation
/quit   - Exit
```
