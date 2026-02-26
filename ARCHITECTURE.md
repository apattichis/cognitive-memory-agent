# Architecture

## A. High-Level Flow

User queries flow through the agent, which assembles context from all active memory systems into a single LLM call.

```mermaid
flowchart LR
    A([User Query]) --> B[<b>CognitiveAgent</b><br/><br/>Working Memory<br/>Semantic Memory<br/>Episodic Memory<br/>Procedural Memory<br/>Consolidation] --> C([Response])
```

## B. Per-Query Pipeline

Each `agent.chat()` call has two stages: **route** the query to the right memory systems, then **assemble** everything into a single LLM call.

### Retrieval Gating

A regex classifier inspects each query and decides which memory systems to activate:

| Query type | Semantic | Episodic | Procedural | Example |
|------------|:--------:|:--------:|:----------:|---------|
| **personal** | | x | | "Do you remember my budget?" |
| **factual** | x | | | "What temperature does the QA-7 run at?" |
| **behavioral / default** | x | x | x | "Recommend a setup for my use case" |

### Response Assembly

Once the relevant memories are retrieved, they are assembled into one LLM call. Episodic and procedural context go into the **system prompt** (`system` parameter); semantic chunks and the user query go into the **messages** array. The semantic chunks are inserted just before the user query so the model sees the retrieved context right before answering.

```mermaid
flowchart TD
    EP[Episodic context] --> SYS[System prompt]
    PROC[Procedural rules] --> SYS

    SEM[Semantic chunks] --> MSG[Messages array]
    Q([User query]) --> MSG

    SYS --> API[Claude API call]
    MSG --> API

    API --> R([Response])
```

### Conflict Detection

When both semantic and episodic memory are active for the same query, an LLM call compares them. If a contradiction is found (e.g., an episodic memory says revenue is $800M but the PDF says $1.2B), a conflict notice is appended to the system prompt so the model can address it transparently.

```mermaid
flowchart LR
    SEM2[Semantic text] --> CD{Conflict Detection}
    EP2[Episodic text] --> CD
    CD -->|contradiction| FLAG[Append notice to system prompt]
    CD -->|none| SKIP[No change]
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
| **Agent** | `agent.py` | Orchestrator - retrieval gating, conflict detection, system prompt assembly | `mode="full"` or `"semantic_only"`, `CONFLICT_DETECTION_ENABLED=True` |
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
