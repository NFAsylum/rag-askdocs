# rag-babel-docs

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NFAsylum/rag-babel-docs/blob/main/notebooks/rag_demo.ipynb)

Retrieval-Augmented Generation over [Babel](https://github.com/NFAsylum/babel-tcc)'s documentation: ingest its README, docs and code samples into a vector store, then answer natural-language questions about the project grounded in that content, with cited sources.

## What is RAG?

**Retrieval-Augmented Generation** answers questions by retrieving relevant text chunks from a knowledge base and feeding them to an LLM as context, instead of relying only on what the model memorized during training. This grounds answers in a specific corpus, reduces hallucination, and lets responses cite exactly which document they came from.

The trade-off versus fine-tuning: RAG needs no retraining when the corpus changes (re-run ingestion), but answer quality depends on retrieval quality — if the right chunk isn't retrieved, the LLM can't use it.

## Architecture

```
                     INGEST (ingest.py)
  ┌──────────────┐   ┌───────────────┐   ┌─────────────────┐   ┌───────────┐
  │ babel-tcc repo│──▶│ chunk (512tok)│──▶│ embed (MiniLM-L6)│──▶│ ChromaDB │
  │ README+docs+  │   │ SentenceSplit │   │ sentence-transf. │   │ (persisted)│
  │ examples      │   └───────────────┘   └─────────────────┘   └───────────┘
  └──────────────┘

                     QUERY (query.py / demo.py)
  ┌──────────┐   ┌────────────────┐   ┌──────────────┐   ┌────────────────┐
  │ question │──▶│ embed question │──▶│ top-k search │──▶│ Claude (Anthropic)│
  └──────────┘   └────────────────┘   │ (k=4, Chroma)│   │ + retrieved ctx  │
                                       └──────────────┘   └────────────────┘
                                                                    │
                                                                    ▼
                                                     answer + cited source files
```

## Dataset

Source: [`NFAsylum/babel-tcc`](https://github.com/NFAsylum/babel-tcc) — Babel is my own TCC project (a multi-language code translation VS Code extension), so this doubles as "a RAG system over the docs of the code Babel itself processes." `ingest.py` shallow-clones the repo and indexes `README.md`, everything under `docs/` (architecture, setup, roadmap, FAQ, etc.), and the code samples under `examples/` (C#, Python, Portugol, VisuAlg) — around 27k words of source material.

## Stack decisions

- **LlamaIndex** — orchestrates chunking, embedding, storage and retrieval without hand-rolling that plumbing, while staying thin enough to see each step explicitly (vs. a heavier agent framework).
- **ChromaDB** — embedded, file-persisted vector store; no external service to run for a single-user demo.
- **sentence-transformers (`all-MiniLM-L6-v2`)** for embeddings — runs locally and free, so the only paid API call in the whole pipeline is the final generation step.
- **Anthropic API (Claude Haiku by default, Sonnet via `ANTHROPIC_MODEL` env var)** for generation — used in production at my previous job, so this pipeline reuses that experience end-to-end.
- **Ollama fallback** — documented here, not implemented: swap `llama_index.llms.anthropic.Anthropic` for `llama_index.llms.ollama.Ollama` in `query.py` to run generation fully locally.

## Setup

```bash
git clone https://github.com/NFAsylum/rag-babel-docs.git
cd rag-babel-docs
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY (get credits at console.anthropic.com)
```

## Usage

```bash
python ingest.py          # clones babel-tcc into data/ and builds the Chroma index
python query.py "What languages does Babel support?"
python demo.py             # interactive CLI loop
```

## Example queries

See [`example_queries.md`](./example_queries.md) for recorded questions and answers with cited sources.

## License

MIT — see [LICENSE](./LICENSE).
