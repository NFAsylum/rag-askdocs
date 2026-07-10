"""Query the RAG pipeline: retrieve top-k chunks, ask an LLM, return sources.

Reads whichever repo was last indexed by ingest.py (chroma_db/active_collection.txt).

The generation backend is selected with the LLM_BACKEND env var:
  - "anthropic" (default): Claude via the Anthropic API. Needs ANTHROPIC_API_KEY.
  - "openai-like": any OpenAI-compatible local server (vLLM, LM Studio, llama.cpp, ...).
Nothing here needs code edits to switch backends — just environment variables.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
CHROMA_DIR = ROOT / "chroma_db"
ACTIVE_COLLECTION_FILE = CHROMA_DIR / "active_collection.txt"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 4

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_LOCAL_BASE_URL = "http://localhost:8090/v1"
DEFAULT_LOCAL_MODEL = "qwen2.5-coder-7b"

NO_ANSWER = "I don't have enough information in the retrieved context to answer that."

# Grounding templates: force the model to answer strictly from retrieved context and
# to abstain otherwise. The "even about projects with a similar name" clause targets the
# main failure mode for small models — overriding the context with parametric priors
# (e.g. confusing an indexed project with a well-known namesake). Applies to any backend.
_QA_TEMPLATE = (
    "You are a documentation assistant answering questions about ONE specific software "
    "repository, using only the retrieved context below.\n"
    "Rules:\n"
    "- Answer strictly from the context. Do not use prior knowledge, even about projects "
    "with a similar name — the indexed project may differ from any namesake you know.\n"
    f'- If the context does not contain the answer, reply exactly: "{NO_ANSWER}"\n'
    "- Be concise and factual.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Question: {query_str}\n"
    "Answer: "
)
_REFINE_TEMPLATE = (
    "You are refining an answer with more retrieved context.\n"
    "Question: {query_str}\n"
    "Existing answer: {existing_answer}\n"
    "Additional context:\n"
    "---------------------\n"
    "{context_msg}\n"
    "---------------------\n"
    "Refine the answer using ONLY the context (no prior knowledge). If the combined context "
    f'still does not answer the question, return exactly: "{NO_ANSWER}"\n'
    "Refined answer: "
)


def active_collection() -> str:
    if not ACTIVE_COLLECTION_FILE.exists():
        raise RuntimeError(f"No index found at {CHROMA_DIR}. Run `python ingest.py` first.")
    return ACTIVE_COLLECTION_FILE.read_text().strip()


def _backend() -> str:
    return os.getenv("LLM_BACKEND", "anthropic").strip().lower()


def build_llm():
    """Construct the generation LLM from env vars. Imports are lazy so switching
    backends never requires the other backend's package to be installed."""
    backend = _backend()
    if backend == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key "
                "(get credits at console.anthropic.com), or set LLM_BACKEND=openai-like "
                "to use a local model."
            )
        from llama_index.llms.anthropic import Anthropic

        return Anthropic(model=os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL), api_key=api_key)

    if backend in {"openai-like", "openailike", "local"}:
        from llama_index.llms.openai_like import OpenAILike

        return OpenAILike(
            model=os.getenv("OPENAI_LIKE_MODEL", DEFAULT_LOCAL_MODEL),
            api_base=os.getenv("OPENAI_LIKE_BASE_URL", DEFAULT_LOCAL_BASE_URL),
            api_key=os.getenv("OPENAI_LIKE_API_KEY", "not-needed"),
            is_chat_model=True,
            context_window=int(os.getenv("OPENAI_LIKE_CONTEXT_WINDOW", "32768")),
        )

    raise RuntimeError(f"Unknown LLM_BACKEND '{backend}' (use 'anthropic' or 'openai-like').")


def model_name() -> str:
    """Raw model identifier of the active backend (used for run filenames)."""
    if _backend() == "anthropic":
        return os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    return os.getenv("OPENAI_LIKE_MODEL", DEFAULT_LOCAL_MODEL)


def model_label() -> str:
    """Human-readable description of the active generation model, for attribution."""
    if _backend() == "anthropic":
        return f"{model_name()} (Anthropic API)"
    base = os.getenv("OPENAI_LIKE_BASE_URL", DEFAULT_LOCAL_BASE_URL)
    return f"{model_name()} (OpenAI-compatible @ {base})"


def build_query_engine():
    import chromadb
    from llama_index.core import PromptTemplate, Settings, VectorStoreIndex
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore

    collection = active_collection()
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.llm = build_llm()

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    chroma_collection = chroma_client.get_or_create_collection(collection)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store)

    return index.as_query_engine(
        similarity_top_k=TOP_K,
        text_qa_template=PromptTemplate(_QA_TEMPLATE),
        refine_template=PromptTemplate(_REFINE_TEMPLATE),
    )


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
