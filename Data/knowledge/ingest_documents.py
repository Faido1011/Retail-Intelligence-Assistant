
from pathlib import Path
import json
import re


# Find the folder containing this Python script
KNOWLEDGE_DIR = Path(__file__).parent

# Input documents and output file
OUTPUT_FILE = KNOWLEDGE_DIR / "processed_chunks.json"

# Chunk settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


def clean_text(text):
    """Clean unnecessary spaces while preserving paragraphs."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_chunks(text):
    """Split text into chunks with a small overlap."""
    words = text.split()
    chunks = []
    current_words = []
    current_length = 0

    for word in words:
        extra_length = len(word) + (1 if current_words else 0)

        if current_words and current_length + extra_length > CHUNK_SIZE:
            chunks.append(" ".join(current_words))

            # Keep some words from the previous chunk for context
            overlap_words = []
            overlap_length = 0

            for previous_word in reversed(current_words):
                extra = len(previous_word) + (
                    1 if overlap_words else 0
                )

                if overlap_length + extra > CHUNK_OVERLAP:
                    break

                overlap_words.insert(0, previous_word)
                overlap_length += extra

            current_words = overlap_words
            current_length = len(" ".join(current_words))

        if current_words:
            current_length += 1

        current_words.append(word)
        current_length += len(word)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def ingest_documents():
    """Read text documents, clean them, chunk them, and save metadata."""
    documents = sorted(
        KNOWLEDGE_DIR.glob("*.txt")
    )

    if not documents:
        print("No .txt documents found in the knowledge folder.")
        return

    all_chunks = []

    for document_path in documents:
        try:
            raw_text = document_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            print(f"Could not read {document_path.name}: {error}")
            continue

        cleaned = clean_text(raw_text)

        if not cleaned:
            print(f"Skipping empty document: {document_path.name}")
            continue

        chunks = split_into_chunks(cleaned)

        # Read the document type from the source, if available
        document_type = "Text Document"

        for line in cleaned.splitlines():
            if line.lower().startswith("document type:"):
                document_type = line.split(":", 1)[1].strip()
                break

        for index, chunk in enumerate(chunks, start=1):
            all_chunks.append({
                "id": f"{document_path.stem}_chunk_{index}",
                "source": document_path.name,
                "document_type": document_type,
                "chunk_index": index,
                "total_chunks": len(chunks),
                "char_count": len(chunk),
                "content": chunk
            })

        print(
            f"Processed {document_path.name}: "
            f"{len(chunks)} chunk(s)"
        )

    # Save source-derived text and metadata separately from AI answers
    OUTPUT_FILE.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\nTotal chunks created: {len(all_chunks)}")
    print(f"Saved processed documents to: {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest_documents()
