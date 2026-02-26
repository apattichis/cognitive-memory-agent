import os

# LLM
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = "claude-sonnet-4-20250514"
TEMPERATURE = 0.7
MAX_TOKENS = 1024

# ChromaDB
CHROMA_PERSIST_DIR = "./chroma_db"

# Semantic memory
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SEMANTIC_TOP_K = 10

# Episodic memory
EPISODIC_TOP_K = 3
RECENCY_HALF_LIFE_HOURS = 72

# Consolidation
CONSOLIDATION_THRESHOLD = 0.70  # similarity threshold for merging
CONSOLIDATION_EVERY_N = 5       # consolidate every N conversations
PROMOTION_MIN_OCCURRENCES = 3   # promote pattern after N appearances

# Procedural memory
PROCEDURAL_MEMORY_FILE = "./procedural_memory.txt"
MAX_PROCEDURAL_RULES = 15

# Conflict detection
CONFLICT_DETECTION_ENABLED = True
