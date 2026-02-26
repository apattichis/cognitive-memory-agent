# Architecture

## A. High-Level Flow

User queries flow through the agent, which assembles context from all active memory systems into a single LLM call.

```mermaid
flowchart LR
    User([User Query]) --> Agent

    subgraph Agent[CognitiveAgent]
        direction TB
        WM[Working Memory<br/>Chat history buffer]
        SM[Semantic Memory<br/>ChromaDB RAG] --> WM
        EM[Episodic Memory<br/>Past conversations] --> WM
        PM[Procedural Memory<br/>Learned rules] --> WM
        CON[Consolidation<br/>Sleep phase]
    end

    Agent --> Response([Response])

    EM -.->|every N convs| CON
    CON -.->|merge| EM
    CON -.->|promote| PM
```

## B. Per-Query Pipeline

Each `agent.chat()` call assembles context from multiple memory systems and sends a single LLM request.

```mermaid
flowchart TD
    Q([User sends query]) --> EP[Episodic Memory<br/>recall past experiences]
    Q --> PR[Procedural Memory<br/>load learned rules]

    EP --> SYS[Build system prompt<br/>base + episodic + procedural]
    PR --> SYS

    Q --> SEM[Semantic Memory<br/>retrieve RAG chunks]

    SYS --> LLM[Claude API call<br/>system prompt + chat history + RAG chunks]
    SEM --> LLM
    Q -->|add to chat history| LLM

    LLM --> R([Return response])
```

## C. Consolidation Pipeline

Triggered every N conversations during `new_conversation()`. Compresses episodic memory and extracts behavioral patterns.

```mermaid
flowchart TD
    START([Sleep triggered]) --> FETCH[Fetch all episodes<br/>with embeddings]
    FETCH --> CLUSTER[Greedy clustering<br/>by cosine similarity]
    CLUSTER --> FILTER{Cluster size >= 2?}

    FILTER -->|Yes| MERGE[LLM merges cluster<br/>into one unified episode]
    MERGE --> DELETE[Delete originals<br/>from ChromaDB]
    DELETE --> STORE[Store merged episode]

    FILTER -->|No| SKIP[Keep as-is]

    STORE --> PROMOTE
    SKIP --> PROMOTE[LLM extracts recurring<br/>patterns from all episodes]
    PROMOTE --> RULES[Add new rules to<br/>procedural memory]
    RULES --> DONE([Consolidation complete])
```

## D. Component Reference

| Module | File | Purpose | Key Config |
|--------|------|---------|------------|
| **Working Memory** | `memory/working.py` | Chat history buffer, Anthropic API calls | `MODEL_NAME`, `MAX_TOKENS`, `TEMPERATURE` |
| **Semantic Memory** | `memory/semantic.py` | PDF ingestion, text chunking, ChromaDB vector search | `CHUNK_SIZE=800`, `CHUNK_OVERLAP=100`, `SEMANTIC_TOP_K=10` |
| **Episodic Memory** | `memory/episodic.py` | LLM reflection on conversations, recency-weighted recall | `EPISODIC_TOP_K=3`, `RECENCY_HALF_LIFE_HOURS=72` |
| **Procedural Memory** | `memory/procedural.py` | Incremental rule updates via LLM synthesis, persisted to JSON | `MAX_PROCEDURAL_RULES=15` |
| **Consolidation** | `memory/consolidation.py` | Clustering, merging, and pattern promotion | `CONSOLIDATION_THRESHOLD=0.70`, `CONSOLIDATION_EVERY_N=5`, `PROMOTION_MIN_OCCURRENCES=3` |
| **Agent** | `agent.py` | Orchestrator - builds system prompt, routes queries | `mode="full"` or `"semantic_only"` |
| **Config** | `config.py` | All constants and hyperparameters | - |

## E. Conversation Lifecycle

Shows the repeating cycle across a multi-conversation session.

```mermaid
flowchart TD
    CHAT([User chats with agent]) --> SAVE[/new_conversation/]
    SAVE --> REFLECT[LLM reflects on conversation]
    REFLECT --> STORE[Store episode in ChromaDB]
    STORE --> UPDATE[Update procedural rules]
    UPDATE --> CHECK{Conversation count<br/>divisible by 5?}
    CHECK -->|No| CHAT
    CHECK -->|Yes| SLEEP[Consolidation - sleep phase]
    SLEEP --> CLUSTER[Cluster similar episodes]
    CLUSTER --> MERGE[Merge overlapping into one]
    MERGE --> PROMOTE[Promote patterns to rules]
    PROMOTE --> CHAT
```
