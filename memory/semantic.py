"""Semantic memory - RAG over documents stored in ChromaDB."""

import os
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config


class SemanticMemory:
    """Factual knowledge base built from documents."""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name="semantic_memory",
            metadata={"hnsw:space": "cosine"},
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""],
        )

    def ingest_pdf(self, pdf_path: str):
        """Load a PDF, chunk it, and store in ChromaDB."""
        filename = os.path.basename(pdf_path)

        # Check if already ingested
        existing = self.collection.get(where={"source": filename})
        if existing["ids"]:
            print(f"  Already ingested: {filename} ({len(existing['ids'])} chunks)")
            return

        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        full_text = "\n\n".join(p.page_content for p in pages)
        chunks = self.splitter.split_text(full_text)

        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )
        print(f"  Ingested: {filename} -> {len(chunks)} chunks")

    def ingest_all(self, data_dir: str = "./data"):
        """Ingest all PDFs from the data directory."""
        if not os.path.exists(data_dir):
            print(f"  No data directory found at {data_dir}")
            return

        pdfs = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
        if not pdfs:
            print("  No PDFs found in data/")
            return

        for pdf in pdfs:
            self.ingest_pdf(os.path.join(data_dir, pdf))

    def recall(self, query: str) -> str | None:
        """Retrieve relevant chunks for a query."""
        if self.collection.count() == 0:
            return None

        results = self.collection.query(
            query_texts=[query],
            n_results=min(config.SEMANTIC_TOP_K, self.collection.count()),
        )

        if not results["documents"][0]:
            return None

        chunks = results["documents"][0]
        formatted = "\n\n".join(
            f"[Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(chunks)
        )
        return formatted

    def recall_as_message(self, query: str) -> dict | None:
        """Retrieve chunks and format as a user message for injection."""
        context = self.recall(query)
        if not context:
            return None

        return {
            "role": "user",
            "content": (
                f"[KNOWLEDGE BASE RETRIEVAL]\n"
                f"The following excerpts were retrieved from your document memory. "
                f"Use ONLY this information to answer factual questions about these topics. "
                f"If the user's question is not covered by these excerpts, say you don't have "
                f"that information in your knowledge base.\n\n{context}"
            ),
        }
