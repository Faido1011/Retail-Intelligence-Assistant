
import json
import re
from pathlib import Path

FOLDER = Path(__file__).parent
JSON_FILE = FOLDER / "processed_chunks.json"

STOP_WORDS = {
    "the", "is", "a", "an", "of", "to", "and", "in",
    "what", "how", "does", "do", "are", "for", "this",
    "that", "it", "by", "on", "with", "was", "were",
    "can", "could", "would", "should", "me", "tell",
    "about", "please", "from", "which", "used"
}


def tokenize(text):
    """Convert text into meaningful lowercase words."""
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]


def search_documents(question, chunks, limit=3):
    """Rank source chunks by meaningful word matches."""
    question_words = set(tokenize(question))

    if not question_words:
        return []

    results = []

    for chunk in chunks:
        content_words = set(tokenize(chunk["content"]))
        matched_words = question_words.intersection(content_words)

        if not matched_words:
            continue

        # Calculate the proportion of question terms found in the chunk
        score = len(matched_words) / len(question_words)

        results.append({
            "source": chunk["source"],
            "chunk_id": chunk["id"],
            "matched_terms": sorted(matched_words),
            "score": round(score, 3),
            "content": chunk["content"]
        })

    # Highest relevance score first
    results.sort(
        key=lambda item: (
            item["score"],
            len(item["matched_terms"])
        ),
        reverse=True
    )

    return results[:limit]


def main():
    if not JSON_FILE.exists():
        print("Processed document file not found.")
        print("Run ingest_documents.py first.")
        return

    with JSON_FILE.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    question = input(
        "Ask a question about the retail documentation: "
    ).strip()

    if not question:
        print("Please enter a question.")
        return

    results = search_documents(question, chunks)

    if not results:
        print(
            "\nNo supporting evidence was found "
            "in the available documents."
        )
        return

    print("\nRelevant source evidence:")

    for result in results:
        print(f"\nSource: {result['source']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Relevance score: {result['score']}")
        print(
            "Matched terms: "
            + ", ".join(result["matched_terms"])
        )
        print(f"Content: {result['content']}")


if __name__ == "__main__":
    main()
