# rag-askdocs

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NFAsylum/rag-askdocs/blob/main/notebooks/rag_demo.ipynb)

Retrieval-Augmented Generation over **any GitHub repository**: point it at a repo, it ingests the docs and code into a vector store, then answers natural-language questions grounded in that content, with cited sources.

The default corpus is [Babel](https://github.com/NFAsylum/babel-tcc) (my TCC — a multi-language code-translation VS Code extension), used throughout as the worked example.

## What is RAG?

**Retrieval-Augmented Generation** answers questions by retrieving relevant text chunks from a knowledge base and feeding them to an LLM as context, instead of relying only on what the model memorized during training. This grounds answers in a specific corpus, reduces hallucination, and lets responses cite exactly which document they came from.

Nothing here is trained. The embedding model and the LLM are both used purely for inference — the corpus lives in the vector index, not in model weights. So when the source repo changes, you re-run ingestion (seconds, no GPU) instead of retraining anything. The trade-off versus fine-tuning: answer quality depends on retrieval quality — if the right chunk isn't retrieved, the LLM can't use it.

## Architecture

```
                     INGEST (ingest.py)
  ┌──────────────┐   ┌───────────────┐   ┌─────────────────┐   ┌───────────┐
  │ any GitHub   │──▶│ chunk (512tok)│──▶│ embed (MiniLM-L6)│──▶│ ChromaDB │
  │ repo (docs + │   │ SentenceSplit │   │ sentence-transf. │   │ (persisted)│
  │ code)        │   └───────────────┘   └─────────────────┘   └───────────┘
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

By default `ingest.py` shallow-clones [`NFAsylum/babel-tcc`](https://github.com/NFAsylum/babel-tcc) and indexes it. Babel is my own project, so I can judge whether answers are actually correct — a known-good corpus to validate retrieval against — and it doubles as "a RAG system over the docs of the code Babel itself processes."

Any public repo works: `python ingest.py --repo https://github.com/OWNER/NAME.git`. Restrict the scope to specific subdirectories with `--dirs docs,examples`; otherwise the whole repo is indexed. It picks up docs (`.md`, `.txt`, `.rst`, `.adoc`) and common source files (`.py`, `.cs`, `.js`, `.ts`, `.java`, `.go`, `.rs`, …), skipping build/vendor directories.

## Stack decisions

- **LlamaIndex** — orchestrates chunking, embedding, storage and retrieval without hand-rolling that plumbing, while staying thin enough to see each step explicitly (vs. a heavier agent framework).
- **ChromaDB** — embedded, file-persisted vector store; no external service to run for a single-user demo. Each ingested repo becomes its own collection.
- **sentence-transformers (`all-MiniLM-L6-v2`)** for embeddings — runs locally and free, so the only paid API call in the whole pipeline is the final generation step.
- **Anthropic API (Claude Haiku by default, Sonnet via `ANTHROPIC_MODEL` env var)** for generation — used in production at my previous job, so this pipeline reuses that experience end-to-end.
- **Local model fallback** — set `LLM_BACKEND=openai-like` to point generation at any OpenAI-compatible local server (vLLM, LM Studio, llama.cpp, ...); no code edits. See [Local model](#local-model) below.

## Setup

```bash
git clone https://github.com/NFAsylum/rag-askdocs.git
cd rag-askdocs
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY (get credits at console.anthropic.com)
```

## Usage

```bash
# index the default corpus (Babel docs + examples)
python ingest.py --dirs docs,examples

# ...or any other repo
python ingest.py --repo https://github.com/OWNER/NAME.git

python query.py "What languages does Babel support?"
python demo.py             # interactive CLI loop
python examples.py         # regenerate example_queries.md from the showcase questions
```

`query.py`, `demo.py` and `examples.py` always target whichever repo was last ingested.

### Local model

By default generation uses the Anthropic API. To run generation on a local OpenAI-compatible
server instead — no code changes — set:

```bash
export LLM_BACKEND=openai-like
export OPENAI_LIKE_BASE_URL=http://localhost:8090/v1   # your server
export OPENAI_LIKE_MODEL=qwen2.5-coder-7b              # your model
python demo.py
```

## Example queries

See [`example_queries.md`](./example_queries.md) for recorded questions and answers with cited
sources, generated by `python examples.py`.

## License

MIT — see [LICENSE](./LICENSE).
