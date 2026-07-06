"""Interactive CLI demo for the Babel docs RAG pipeline."""
from query import build_query_engine


def main() -> None:
    print("Babel Docs RAG — ask a question, or type 'exit' to quit.\n")
    engine = build_query_engine()
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        response = engine.query(question)
        print(f"\n{response}\n")
        print("Sources:")
        for node in response.source_nodes:
            score = f"{node.score:.3f}" if node.score is not None else "n/a"
            print(f"  - {node.metadata.get('file_name', 'unknown')} (score={score})")
        print()


if __name__ == "__main__":
    main()
