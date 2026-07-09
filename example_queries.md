# Example queries

Recorded output of `python query.py "<question>"` against the default corpus (Babel's `docs/` + `examples/`). Answers and cited sources below are exactly what the pipeline returned — nothing here is hand-written.

**Pending:** this file needs a real `ANTHROPIC_API_KEY` (or a local LLM fallback) to run the generation step and populate. Retrieval already works with no key — verified that these questions retrieve the right source files:

| Question | Top retrieved source |
| --- | --- |
| What is Babel? | `troubleshooting.md`, `adding-new-language.md` |
| How do I add support for a new IDE? | `adding-new-ide.md` |
| Which languages does Babel translate? | `plano-geral.txt`, `faq.md` |

Planned questions to record (same set as `notebooks/rag_demo.ipynb`):

1. What is Babel and what problem does it solve?
2. Which programming languages does Babel support for translation?
3. How do I add support for a new IDE to Babel?
4. _(to fill in — pick 2 more that exercise different doc sections, e.g. architecture or setup)_
