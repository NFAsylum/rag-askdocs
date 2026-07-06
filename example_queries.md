# Example queries

Recorded output of `python query.py "<question>"` against the ingested Babel docs. Answers and cited sources below are exactly what the pipeline returned — nothing here is hand-written.

**Pending:** this file needs a real `ANTHROPIC_API_KEY` to run and populate. Retrieval (embedding + ChromaDB) works with no key; only the final generation call needs one.

Planned questions (same set as `notebooks/rag_demo.ipynb`):

1. What is Babel and what problem does it solve?
2. Which programming languages does Babel support for translation?
3. How do I add support for a new IDE to Babel?
4. _(to fill in — pick 2 more that exercise different doc sections, e.g. architecture or setup)_
