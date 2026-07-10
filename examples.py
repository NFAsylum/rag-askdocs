"""Run the canonical showcase questions and record one file per model in example_runs/.

The generated file is a recorded artifact — every answer is real pipeline output, not
hand-written. It is named after the active model and carries the model + date in its header.
The curated comparison lives in example_queries.md (maintained by hand). Re-run after
changing the corpus or the model:

    python examples.py                                  # name/label from the active backend
    python examples.py --model-label "qwen3.6-35b-a3b-thinking"
"""
import argparse
import re
from datetime import date
from pathlib import Path

from query import model_label, model_name, query

EXAMPLE_RUNS_DIR = Path(__file__).parent / "example_runs"

QUESTIONS = [
    "What is Babel and what problem does it solve?",
    "Which programming languages does Babel support for translation?",
    "How do I add support for a new IDE to Babel?",
    "How do I install and set up Babel?",
    "What is Babel's architecture?",
]


def slugify(text: str) -> str:
    """Filesystem-safe slug for a run filename."""
    return re.sub(r"[^a-z0-9._-]+", "-", text.strip().lower()).strip("-") or "run"


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
    parser = argparse.ArgumentParser(description="Record a per-model run into example_runs/")
    parser.add_argument(
        "--model-label",
        default=None,
        help="Override the model name in the header and filename (default: active backend)",
    )
    args = parser.parse_args()

    label = args.model_label or model_label()
    slug = slugify(args.model_label or model_name())
    EXAMPLE_RUNS_DIR.mkdir(exist_ok=True)
    out_file = EXAMPLE_RUNS_DIR / f"{slug}.md"
    out_file.write_text(render(label))
    print(f"Wrote {out_file} ({len(QUESTIONS)} questions, model: {label})")


if __name__ == "__main__":
    main()
