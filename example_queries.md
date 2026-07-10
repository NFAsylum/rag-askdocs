# Example queries — results overview

Five questions run through the pipeline over the default corpus (Babel's `docs/` + `examples/`),
with two local models. The full recorded outputs (real pipeline output, not hand-written) live in
[`example_runs/`](./example_runs); this page summarizes how each answer holds up when **verified
against Babel's own documentation**.

| # | Question | `qwen2.5-coder-7b` | `qwen3.6-35b` | Verified against |
|---|----------|:------------------:|:-------------:|------------------|
| 1 | What is Babel and what problem does it solve? | abstained | ✅ correct | `faq.md`, `architecture.md` |
| 2 | Which programming languages does Babel support? | ❌ wrong | ❌ wrong | `faq.md` — see note below |
| 3 | How do I add support for a new IDE? | ✅ correct | ✅ correct | `adding-new-ide.md` |
| 4 | How do I install and set up Babel? | abstained | ✅ correct | `setup-ambiente.md` |
| 5 | What is Babel's architecture? | abstained | ✅ correct | `architecture.md` |

**Reading this:** the 35B model answers 4/5 correctly; the 7B model, under the grounding prompt,
safely abstains rather than hallucinate on questions it can't ground (3/5). Both miss Q2 — and that
miss is the interesting one.

**Q2 is a documented failure, not a fluke.** The shipped answer (`faq.md`) is C#, Python, VisuAlg,
Portugol Studio. Both models answer "C#, Python, JavaScript, Java" because they retrieved Babel's
internal *planning* docs, which list JavaScript/Java as future roadmap structure — and the pipeline
can't tell a roadmap from a reference doc. See
[Limitations](./README.md#limitations--where-this-rag-breaks-and-why) for the full analysis.

Recorded runs:
- [`example_runs/qwen2.5-coder-7b.md`](./example_runs/qwen2.5-coder-7b.md)
- [`example_runs/qwen3.6-35b-a3b-thinking.md`](./example_runs/qwen3.6-35b-a3b-thinking.md)
