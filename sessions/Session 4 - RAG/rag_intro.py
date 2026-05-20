"""
===================================================
  RAG (Retrieval-Augmented Generation) - Intro
===================================================

WHAT IS RAG?
------------
Large Language Models (LLMs) have a knowledge cutoff and no access to your
private data. RAG solves this by:

  1. INDEXING   — chunking your documents and storing them as vectors
  2. RETRIEVAL  — finding the most relevant chunks for a user query
  3. GENERATION — passing those chunks as context to an LLM to produce an answer

PIPELINE OVERVIEW:

  PDF files on disk
      │
      ▼
  [PDF Loader]  ──► raw text
      │
      ▼
  [Chunker]     ──► text chunks
      │
      ▼
  [Embedder]    ──► vectors  ──► [ChromaDB  (persisted to ./chroma_db/)]
                                        │
  User Query    ──► [Embedder] ──► similarity search
                                        │
                                        ▼
                                  top-k chunks  ──► [LLM] ──► Answer


DEPENDENCIES (install once):
  pip install openai python-dotenv chromadb reportlab pypdf
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import os
import textwrap
from pathlib import Path
from typing import List

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from openai import OpenAI
import pypdf

load_dotenv()  # reads OPENAI_API_KEY from .env

PDF_DIR   = Path("pdfs")        # generated PDF files land here
CHROMA_DIR = Path("chroma_db")  # ChromaDB persists its data here
COLLECTION_NAME = "solar_system"


# ---------------------------------------------------------------------------
# STEP 1 — Discover PDFs from the pdfs/ directory
# ---------------------------------------------------------------------------

def get_pdf_files() -> List[Path]:
    """Discover all PDF files in the pdfs/ directory."""
    PDF_DIR.mkdir(exist_ok=True)
    return sorted(PDF_DIR.glob("*.pdf"))


# ---------------------------------------------------------------------------
# STEP 2 — Load text from PDFs with pypdf
# ---------------------------------------------------------------------------

def load_pdf_text(path: Path) -> str:
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# ---------------------------------------------------------------------------
# STEP 3 — Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    text = text.strip()
    chunks: List[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# STEP 5 — ChromaDB vector store
# ---------------------------------------------------------------------------
# ChromaDB is a production-ready, open-source vector database.
# Here we use a PersistentClient so the index survives across Python runs.
#
# OpenAIEmbeddingFunction tells ChromaDB to call the OpenAI Embeddings API
# (text-embedding-3-small) for both documents and queries automatically —
# you never have to call the embedder manually.

def build_vector_store(
    chunks: List[str],
    chunk_ids: List[str],
    persist_dir: Path,
) -> chromadb.Collection:
    persist_dir.mkdir(exist_ok=True)

    embed_fn = OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-3-small",
    )

    client     = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},  # use cosine similarity
    )

    # Add in batches of 100 to stay within ChromaDB's default limits
    BATCH = 100
    for i in range(0, len(chunks), BATCH):
        collection.add(
            documents=chunk_ids[i : i + BATCH],  # stored metadata
            ids=chunk_ids[i : i + BATCH],
        )
        # Store the actual text in the documents field
        # (overwrite with upsert to support re-runs)
    collection.upsert(
        documents=chunks,
        ids=chunk_ids,
    )

    print(f"  [ChromaDB] Upserted {len(chunks)} chunks → {persist_dir}")
    return collection


# ---------------------------------------------------------------------------
# STEP 6 — Generation
# ---------------------------------------------------------------------------
# The retrieved chunks become "context" injected into the LLM system prompt.
# The model is instructed to answer ONLY from that context (grounding).

def generate_answer(
    query: str,
    context_chunks: List[str],
    client: OpenAI,
) -> str:
    context_text = "\n\n---\n\n".join(context_chunks)

    system_prompt = (
        "You are a helpful assistant. Answer the user's question using ONLY "
        "the information provided in the CONTEXT below. "
        "If the answer is not present in the context, say "
        "'I don't have enough information to answer that.'"
    )
    user_prompt = f"""CONTEXT:\n{context_text}\n\nQUESTION:\n{query}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# STEP 7 — Full RAG Pipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    """
    End-to-end RAG pipeline:
      discover PDFs  →  load & chunk  →  ChromaDB  →  OpenAI generation

    Usage:
        rag = RAGPipeline()
        print(rag.ask("Which planet has the tallest volcano?"))
    """

    def __init__(self):
        self.openai_client = OpenAI()

        print("\n[Step 1/3] Discovering PDF files ...")
        pdf_paths = get_pdf_files()
        if not pdf_paths:
            raise FileNotFoundError(f"No PDF files found in {PDF_DIR.resolve()}")

        # 2. Load, extract, and chunk all PDFs
        print("\n[Step 2/3] Loading & chunking PDFs ...")
        all_chunks: List[str] = []
        all_ids:    List[str] = []
        for pdf_path in pdf_paths:
            text   = load_pdf_text(pdf_path)
            chunks = chunk_text(text)
            stem   = pdf_path.stem
            ids    = [f"{stem}::chunk{i}" for i in range(len(chunks))]
            all_chunks.extend(chunks)
            all_ids.extend(ids)
            print(f"  [Loader] {pdf_path.name} → {len(chunks)} chunks")

        # 3. Index into ChromaDB
        print("\n[Step 3/3] Indexing into ChromaDB ...")
        self.collection = build_vector_store(all_chunks, all_ids, CHROMA_DIR)
        print("\n[Pipeline] Ready.\n")

    def ask(self, query: str, top_k: int = 4) -> str:
        # Retrieve — ChromaDB embeds the query and returns similar chunks
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )
        retrieved_chunks: List[str] = results["documents"][0]

        # Generate — pass chunks as grounding context to the LLM
        return generate_answer(query, retrieved_chunks, self.openai_client)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  RAG Demo — Solar System (PDF knowledge base + ChromaDB)")
    print("=" * 60)

    rag = RAGPipeline()

    print("\nAsk a question about the Solar System.")
    print("Press Enter on an empty line or type 'exit' to quit.")

    while True:
        question = input("\nQ: ").strip()
        if not question or question.lower() in {"exit", "quit"}:
            print("\nExiting RAG demo.")
            break

        answer = rag.ask(question)
        wrapped = textwrap.fill(f"A: {answer}", width=72, subsequent_indent="   ")
        print(wrapped)
        print("-" * 60)
