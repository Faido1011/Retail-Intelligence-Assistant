
import json
from pathlib import Path

import chromadb
import requests

# Locate files relative to this script
BASE_DIR = Path(__file__).resolve().parent
CHUNKS_FILE = BASE_DIR / "processed_chunks.json"
DB_DIR = BASE_DIR / "chroma_db"

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "embeddinggemma:latest"
COLLECTION_NAME = "retail_knowledge"


def get_embeddings(texts):
    """Generate embeddings using the local Ollama server."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBED_MODEL,
            "input": texts,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    embeddings = data.get("embeddings", [])
    if len(embeddings) != len(texts):
        raise ValueError(
            f"Expected {len(texts)} embeddings, "
            f"but received {len(embeddings)}."
        )

    return embeddings


def main():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {CHUNKS_FILE}"
        )

    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not chunks:
        raise ValueError("No document chunks were found.")

    print(f"Loaded {len(chunks)} chunks.")

    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Remove old entries so rerunning this script rebuilds the index.
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    batch_size = 16

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        texts = [item["content"] for item in batch]
        embeddings = get_embeddings(texts)

        ids = [str(item["id"]) for item in batch]
        metadatas = []

        for item in batch:
            metadatas.append({
                "source": str(item.get("source", "unknown")),
                "document_type": str(
                    item.get("document_type", "text")
                ),
                "chunk_index": int(item.get("chunk_index", 0)),
                "total_chunks": int(item.get("total_chunks", 1)),
            })

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(
            f"Indexed {min(start + batch_size, len(chunks))}"
            f"/{len(chunks)} chunks."
        )

    print("\nRAG index built successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Stored chunks: {collection.count()}")
    print(f"Index folder: {DB_DIR}")


if __name__ == "__main__":
    main()
