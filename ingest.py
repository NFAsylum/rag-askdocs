"""Clone Babel's docs and index them into a persisted ChromaDB collection."""
import argparse
import os
import shutil
import subprocess
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

BABEL_REPO = "https://github.com/NFAsylum/babel-tcc.git"
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data" / "babel-tcc"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "babel_docs"

ROOT_FILES = ["README.md"]
INCLUDE_DIRS = ["docs", "examples"]
INCLUDE_EXTS = {".md", ".txt", ".cs", ".py", ".por", ".alg"}


def clone_babel(reclone: bool) -> None:
    if DATA_DIR.exists():
        if not reclone:
            print(f"Using existing clone at {DATA_DIR}")
            return
        shutil.rmtree(DATA_DIR)
    DATA_DIR.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", BABEL_REPO, str(DATA_DIR)], check=True)


def collect_files() -> list[Path]:
    files = [DATA_DIR / name for name in ROOT_FILES if (DATA_DIR / name).exists()]
    for dirname in INCLUDE_DIRS:
        base = DATA_DIR / dirname
        if not base.exists():
            continue
        files.extend(p for p in base.rglob("*") if p.is_file() and p.suffix in INCLUDE_EXTS)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Babel's docs into ChromaDB")
    parser.add_argument("--reclone", action="store_true", help="Force a fresh clone of babel-tcc")
    args = parser.parse_args()

    clone_babel(reclone=args.reclone)
    files = collect_files()
    print(f"Found {len(files)} source files (README + docs/ + examples/)")

    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    documents = SimpleDirectoryReader(input_files=[str(f) for f in files]).load_data()
    print(f"Loaded {len(documents)} documents")

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Indexed into {CHROMA_DIR} (collection: {COLLECTION_NAME})")


if __name__ == "__main__":
    main()
