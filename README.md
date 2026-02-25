# Cognitive Memory Agent

A Python chatbot with four memory systems inspired by cognitive architectures, plus a consolidation mechanism that merges, compresses, and promotes knowledge across memory types.

## Memory Systems

- **Working Memory** - Current conversation context (chat history buffer)
- **Semantic Memory** - RAG over documents via ChromaDB with cosine similarity search
- **Episodic Memory** - Past conversation storage with LLM-generated reflections and recency-weighted retrieval
- **Procedural Memory** - Self-updating behavioral rules that evolve incrementally with experience
- **Consolidation** - Periodic "sleep" phase that clusters similar episodes, merges them, and promotes recurring patterns to procedural rules

## Setup

```bash
# Create conda environment
conda create -n cognitive-memory python=3.11 -y
conda activate cognitive-memory

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key"

# Run the agent
python demo.py
```

## Usage

Drop any PDF into the `data/` directory and the agent will ingest it on startup.

```
You: What temperature does the QA-7 operate at?
Agent: The QA-7 operates at exactly 22.4 degrees Celsius...

/new      - Start a new conversation (saves episodic memory)
/ingest   - Reload documents from data/
/sleep    - Manually trigger memory consolidation
/quit     - Save and exit
```

## Architecture

```
agent.py                  # Orchestrator - builds system prompt from all memory sources
memory/
  working.py              # Chat history buffer + Anthropic API calls
  semantic.py             # PDF ingestion, chunking, ChromaDB vector retrieval
  episodic.py             # Conversation reflection, storage, recency-weighted recall
  procedural.py           # Incremental rule updates via LLM synthesis
  consolidation.py        # Clustering, merging, and pattern promotion
config.py                 # All constants and hyperparameters
demo.py                   # CLI chat interface
```

## How Consolidation Works

Every N conversations (configurable), the agent runs a "sleep" cycle:

1. **Cluster** - Groups episodic memories by embedding cosine similarity
2. **Merge** - LLM synthesizes each cluster into one unified memory, deletes originals
3. **Promote** - Extracts recurring patterns across episodes and adds them as procedural rules

This prevents unbounded memory growth and improves retrieval quality over time.
