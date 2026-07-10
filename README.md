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
- **Grounding prompt** — the query engine uses a custom prompt that forces answers to come only from retrieved context, abstains when the answer isn't there, and explicitly ignores prior knowledge about similarly-named projects. This matters most for small local models, which otherwise tend to answer from parametric memory instead of the retrieved docs.

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

See [`example_queries.md`](./example_queries.md) for a results overview (5 questions, verified
against Babel's docs), and [`example_runs/`](./example_runs) for the full recorded outputs of
each model, generated by `python examples.py`.

## Limitations — where this RAG breaks (and why)

Building this pipeline surfaced RAG's real failure modes. Documenting them honestly, since
knowing *when* RAG fails matters more than pretending it doesn't.

**1. RAG can't tell a roadmap from a reference doc.** Asked *"which programming languages does
Babel support?"*, both local models answer "C#, Python, JavaScript, Java." The shipped answer is
C#, Python, VisuAlg, Portugol Studio (`faq.md`). The extra languages come from Babel's internal
*planning* docs (`repos.txt`, `plano-geral.txt`), which sketch a future repo layout that includes
JavaScript/Java. Those docs aren't wrong — they describe design intent, not shipped state. The
failure is on the RAG side: naive wholesale ingestion drops planning docs and reference docs into
the same pool, and retrieval treats a roadmap's directory listing as current fact — the model
weights whichever chunk has the strongest lexical match, not whichever is authoritative
([Towards Data Science](https://towardsdatascience.com/your-rag-system-retrieves-the-right-data-but-still-produces-wrong-answers-heres-why-and-how-to-fix-it/)),
and current models remain limited at the multi-document analytical reasoning that resolving source
authority would require ([arXiv 2411.16116](https://arxiv.org/abs/2411.16116)). Fixes live in the
pipeline, not the source: scope ingestion to reference docs (`--dirs docs/user-guide`), or add
provenance/authority signals to retrieval — neither fully reliable.

**2. Small models under-utilize retrieved context.** With the grounding prompt,
`qwen2.5-coder-7b` correctly abstains on 3/5 questions rather than hallucinate — safe, but it
fails to synthesize answers that *are* present in the retrieved context. The 35B model answers all
five. Grounding faithfulness scales with model size.

**3. RAG's value is data- and scale-dependent.** For a small, static, ~40-doc corpus like this, a
good search interface would often suffice; RAG earns its cost when answers require synthesis across
many documents or conversational access. Retrieval quality — not prompts or model choice — is the
#1 driver of RAG success ([webbycrown](https://www.webbycrown.com/hybrid-search-for-rag/)), and
governed data reaches 85–92% accuracy versus 45–60% on ungoverned sources
([FluxHuman](https://fluxhuman.com/en/blog/rag-right-data-wrong-answers-fixing-knowledge-conflicts-in-enterp)).

## License

MIT — see [LICENSE](./LICENSE).
