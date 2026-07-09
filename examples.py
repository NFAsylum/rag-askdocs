"""Run the canonical showcase questions and (re)generate example_queries.md.

The generated file is a recorded artifact — every answer below is real output from
the pipeline, not hand-written. Re-run this after changing the corpus or the model:

    python examples.py                                  # label taken from the active backend
    python examples.py --model-label "Qwen2.5-Coder-7B (local)"
"""
import argparse
from datetime import date
from pathlib import Path

from query import model_label, query

OUTPUT_FILE = Path(__file__).parent / "example_queries.md"

QUESTIONS = [
    "What is Babel and what problem does it solve?",
    "Which programming languages does Babel support for translation?",
    "How do I add support for a new IDE to Babel?",
    "How do I install and set up Babel?",
    "What is Babel's architecture?",
]


def render(label: str) -> str:
    lines = [
        "# Example queries",
        "",
        "Recorded output of the RAG pipeline over the default corpus (Babel's `docs/` + "
        "`examples/`). Every answer below is real pipeline output — nothing here is "
        "hand-written. Regenerate with `python examples.py`.",
        "",
        f"- **Generation model:** {label}",
        f"- **Generated on:** {date.today().isoformat()}",
        "",
    ]
    for q in QUESTIONS:
        result = query(q)
        sources = ", ".join(f"`{s['file']}`" for s in result["sources"]) or "_none_"
        lines += [f"## {q}", "", result["answer"].strip(), "", f"**Sources:** {sources}", ""]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate example_queries.md from the pipeline")
    parser.add_argument(
        "--model-label",
        default=None,
        help="Override the model name recorded in the file (default: active backend)",
    )
    args = parser.parse_args()

    label = args.model_label or model_label()
    OUTPUT_FILE.write_text(render(label))
    print(f"Wrote {OUTPUT_FILE} ({len(QUESTIONS)} questions, model: {label})")


if __name__ == "__main__":
    main()
