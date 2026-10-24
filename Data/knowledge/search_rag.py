
from pathlib import Path

import chromadb
import requests

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "embeddinggemma:latest"
COLLECTION_NAME = "retail_knowledge"


def embed_query(question):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBED_MODEL,
            "input": [question],
        },
        timeout=120,
    )
    response.raise_for_status()

    embeddings = response.json().get("embeddings", [])
    if not embeddings:
        raise ValueError("Ollama returned no query embedding.")

    return embeddings[0]


def search_knowledge(question, top_k=3):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    if collection.count() == 0:
        print("The knowledge index is empty.")
        return []

    query_embedding = embed_query(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    for i, content in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        matches.append({
            "content": content,
            "source": metadata.get("source", "unknown"),
            "chunk_index": metadata.get("chunk_index", -1),
            "distance": distance,
        })

    return matches


def main():
    print("Retail Knowledge — Semantic Search")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            print("Please enter a question.\n")
            continue

        

def main():
    print("Retail Knowledge - Semantic Search")
    print("Type 'exit' to quit.\n")

    MAX_COSINE_DISTANCE = 0.75

    while True:
        question = input("Your question: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            print("Please enter a question.\n")
            continue

        try:
            matches = search_knowledge(question)

            # Keep only results that meet the relevance threshold.
            matches = [
                item for item in matches
                if item["distance"] <= MAX_COSINE_DISTANCE
            ]

            if not matches:
                print(
                    "No sufficiently relevant supporting evidence "
                    "was found in the available documents.\n"
                )
                continue

            print("\nRetrieved evidence:")

            for number, item in enumerate(matches, start=1):
                print(f"\n--- Result {number} ---")
                print(f"Source: {item['source']}")
                print(f"Chunk: {item['chunk_index']}")
                print(f"Cosine distance: {item['distance']:.4f}")
                print(item["content"])

        except requests.RequestException as error:
            print(f"Ollama request failed: {error}")

        except Exception as error:
            print(f"Search failed: {error}")

        print()


if __name__ == "__main__":
    main()
