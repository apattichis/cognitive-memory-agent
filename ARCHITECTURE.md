# Architecture

## A. High-Level Flow

User queries flow through the agent, which assembles context from all active memory systems into a single LLM call.

```mermaid
flowchart LR
    User([User Query]) --> Agent
    Agent --> Response([Response])

    subgraph Agent[CognitiveAgent]
        direction LR
        SM[Semantic Memory] -->|RAG chunks| BUILD
        EM[Episodic Memory] -->|past experiences| BUILD
        PM[Procedural Memory] -->|learned rules| BUILD
        BUILD[Build Prompt] --> WM[Working Memory<br/>+ Claude API]
    end

    WM -.->|new_conversation| EM
    EM -.->|every 5 convs| CON[Consolidation]
    CON -.->|merge| EM
    CON -.->|promote| PM
```

## B. Per-Query Pipeline

Each `agent.chat()` call assembles context from multiple memory systems and sends a single LLM request.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant EM as Episodic Memory
    participant PM as Procedural Memory
    participant SM as Semantic Memory
    participant WM as Working Memory
    participant LLM as Claude API

    U->>A: chat(query)

    par Build system prompt
        A->>EM: recall_as_context(query)
        EM-->>A: past experiences
        A->>PM: get_rules_text()
        PM-->>A: behavioral rules
    end
    Note over A: System prompt =<br/>base + episodic + procedural

    A->>SM: recall_as_message(query)
    SM-->>A: RAG chunks as extra message

    A->>WM: add_user_message(query)
    WM->>LLM: system prompt + chat history + RAG chunks
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

Shows what happens across a multi-conversation session.

```mermaid
flowchart LR
    subgraph Conv1[Conversation 1]
        Q1[User queries] --> R1[Agent responds]
    end

    subgraph Save1[new_conversation]
        R1 --> REFL1[LLM reflects on conv]
        REFL1 --> EP1[Store episode in ChromaDB]
        EP1 --> PROC1[Update procedural rules]
    end

    subgraph Conv2[Conversations 2-4]
        Q2[More queries] --> R2[Responses use<br/>episodic + procedural context]
    end

    Save1 --> Conv2

    subgraph Conv5[Conversation 5]
        Q5[Queries] --> R5[Responses]
    end

    Conv2 --> Conv5

    subgraph Sleep[Consolidation - sleep phase]
        CLUST[Cluster similar episodes] --> MERG[Merge overlapping]
        MERG --> PROM[Promote patterns to rules]
    end

    Conv5 -->|triggers| Sleep
    Sleep --> NEXT([Continue with compressed memory])
```
