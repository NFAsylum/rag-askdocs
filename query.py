"""Query the Babel docs RAG pipeline: retrieve top-k chunks, ask Claude, return sources."""
import os
import sys
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

ROOT = Path(__file__).parent
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "babel_docs"
TOP_K = 4
DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


def build_query_engine():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key "
            "(get credits at console.anthropic.com)."
        )
    if not CHROMA_DIR.exists():
        raise RuntimeError(f"No index found at {CHROMA_DIR}. Run `python ingest.py` first.")

    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.llm = Anthropic(model=DEFAULT_MODEL, api_key=api_key)

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store)

    return index.as_query_engine(similarity_top_k=TOP_K)


def query(question: str) -> dict:
    engine = build_query_engine()
    response = engine.query(question)
    sources = [
        {
            "file": node.metadata.get("file_name", "unknown"),
            "score": round(node.score, 3) if node.score is not None else None,
        }
        for node in response.source_nodes
    ]
    return {"answer": str(response), "sources": sources}


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is Babel?"
    result = query(question)
    print(result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        print(f"  - {source['file']} (score={source['score']})")
