"""Clone any GitHub repo and index its docs/code into a persisted ChromaDB collection.

Defaults to NFAsylum/babel-tcc as the showcase corpus, but `--repo <url>` points it
at any public GitHub repository.
"""
import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

DEFAULT_REPO = "https://github.com/NFAsylum/babel-tcc.git"
ROOT = Path(__file__).parent
DATA_ROOT = ROOT / "data"
CHROMA_DIR = ROOT / "chroma_db"
ACTIVE_COLLECTION_FILE = CHROMA_DIR / "active_collection.txt"

# Doc + common source extensions. Broad enough to be useful on an arbitrary repo,
# without pulling in binaries or lockfiles.
INCLUDE_EXTS = {
    ".md", ".txt", ".rst", ".adoc",
    ".py", ".cs", ".js", ".ts", ".java", ".go", ".rs", ".rb", ".php", ".cpp", ".c", ".h",
    ".por", ".alg",
}
# Directories that never carry useful RAG content — skipped during the walk.
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "bin", "obj",
    "dist", "build", "out", "target", ".idea", ".vscode", "images", "assets",
}


def repo_slug(repo_url: str) -> str:
    """Derive a filesystem/collection-safe name from a repo URL."""
    name = repo_url.rstrip("/").split("/")[-1]
    return re.sub(r"\.git$", "", name)


def collection_name(slug: str) -> str:
    """Chroma collection names must be alnum/._- and 3-63 chars."""
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", slug)
    return f"repo_{safe}"[:63]


def clone_repo(repo_url: str, data_dir: Path, reclone: bool) -> None:
    if data_dir.exists():
        if not reclone:
            print(f"Using existing clone at {data_dir}")
            return
        shutil.rmtree(data_dir)
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", repo_url, str(data_dir)], check=True)


def collect_files(data_dir: Path, only_dirs: list[str] | None) -> list[Path]:
    bases = [data_dir / d for d in only_dirs] if only_dirs else [data_dir]
    files: list[Path] = []
    for base in bases:
        if not base.exists():
            print(f"  warning: '{base.relative_to(data_dir)}' not found in repo, skipping")
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in INCLUDE_EXTS:
                continue
            if any(part in SKIP_DIRS for part in path.relative_to(data_dir).parts):
                continue
            files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a GitHub repo's docs/code into ChromaDB")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Git URL to index (default: babel-tcc)")
    parser.add_argument(
        "--dirs",
        default="",
        help="Comma-separated subdirs to restrict indexing to (default: whole repo)",
    )
    parser.add_argument("--reclone", action="store_true", help="Force a fresh clone")
    args = parser.parse_args()

    slug = repo_slug(args.repo)
    data_dir = DATA_ROOT / slug
    collection = collection_name(slug)
    only_dirs = [d.strip() for d in args.dirs.split(",") if d.strip()] or None

    clone_repo(args.repo, data_dir, reclone=args.reclone)
    files = collect_files(data_dir, only_dirs)
    scope = f"dirs={only_dirs}" if only_dirs else "whole repo"
    print(f"Found {len(files)} source files in {slug} ({scope})")
    if not files:
        raise SystemExit("No indexable files found — check --repo / --dirs.")

    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    documents = SimpleDirectoryReader(input_files=[str(f) for f in files]).load_data()
    print(f"Loaded {len(documents)} documents")

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    # Rebuild cleanly so re-ingesting the same repo doesn't stack duplicate chunks.
    # chroma >=0.6 returns collection names (str); older versions return objects.
    existing = [c if isinstance(c, str) else c.name for c in chroma_client.list_collections()]
    if collection in existing:
        chroma_client.delete_collection(collection)
    chroma_collection = chroma_client.get_or_create_collection(collection)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    ACTIVE_COLLECTION_FILE.write_text(collection)
    print(f"Indexed into {CHROMA_DIR} (collection: {collection})")


if __name__ == "__main__":
    main()
