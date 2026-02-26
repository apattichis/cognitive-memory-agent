# Architecture

## A. High-Level Flow

User queries pass through all five memory systems before generating a response.

```mermaid
flowchart LR
    User([User Query]) --> Agent

    subgraph Agent[CognitiveAgent]
        direction TB
        WM[Working Memory<br/>Chat history buffer]
        SM[Semantic Memory<br/>ChromaDB RAG]
        EM[Episodic Memory<br/>Past conversations]
        PM[Procedural Memory<br/>Learned rules]
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
sequenceDiagram
    participant U as User
    participant A as Agent
    participant WM as Working Memory
    participant SM as Semantic Memory
    participant EM as Episodic Memory
    participant PM as Procedural Memory
    participant LLM as Claude API

    U->>A: chat(query)
    A->>EM: recall_as_context(query)
    EM-->>A: past experiences
    A->>PM: get_rules_text()
    PM-->>A: behavioral rules
    A->>A: Build system prompt<br/>(base + episodic + procedural)
    A->>SM: recall_as_message(query)
    SM-->>A: RAG chunks (extra message)
    A->>WM: add_user_message(query)
    WM->>LLM: system prompt + history + RAG context
    LLM-->>WM: response
    WM-->>A: response text
    A-->>U: response
```

## C. Consolidation Pipeline

Triggered every N conversations during `new_conversation()`. Compresses episodic memory and extracts behavioral patterns.

```mermaid
flowchart TD
    START([Sleep triggered]) --> FETCH[Fetch all episodes<br/>with embeddings]
    FETCH --> CLUSTER[Greedy clustering<br/>by cosine similarity]
    CLUSTER --> FILTER{Cluster size >= 2?}

    FILTER -->|Yes| MERGE[LLM merges cluster<br/>into one episode]
    MERGE --> DELETE[Delete originals<br/>from ChromaDB]
    DELETE --> STORE[Store merged episode]

    FILTER -->|No| KEEP[Keep as-is]

    STORE --> PROMOTE[LLM extracts recurring<br/>patterns from all episodes]
    KEEP --> PROMOTE
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

## E. Memory Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PDF: data/ directory
    PDF --> SemanticChunks: ingest (startup)

    [*] --> UserQuery: user sends message
    UserQuery --> WorkingMemory: add to history
    UserQuery --> SemanticRetrieval: vector search
    SemanticRetrieval --> LLMCall: injected as extra message
    WorkingMemory --> LLMCall: chat history
    EpisodicContext --> SystemPrompt: past experiences
    ProceduralRules --> SystemPrompt: learned rules
    SystemPrompt --> LLMCall
    LLMCall --> Response

    Response --> WorkingMemory: stored in buffer

    state "new_conversation()" as NC {
        WorkingMemory --> EpisodicStore: LLM reflection
        EpisodicStore --> ProceduralUpdate: incremental rules
    }

    state "consolidation (every 5 convs)" as CON {
        EpisodicStore --> Cluster: group by similarity
        Cluster --> Merge: compress overlapping
        Merge --> Promote: extract patterns
        Promote --> ProceduralRules
    }
```
