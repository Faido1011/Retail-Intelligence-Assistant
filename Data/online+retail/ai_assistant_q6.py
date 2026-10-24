
import json
import sys
from pathlib import Path

import pandas as pd
import requests
import re
# Q6: Knowledge and Document Processing
KNOWLEDGE_DIR = (
    Path(__file__).parent.parent / "knowledge"
)
CHUNKS_FILE = KNOWLEDGE_DIR / "processed_chunks.json"


def load_knowledge_chunks():
    """Load processed source documents and their metadata."""
    if not CHUNKS_FILE.exists():
        print("Knowledge chunks not found:", CHUNKS_FILE)
        print("Run ingest_documents.py before using document retrieval.")
        return []

    try:
        with CHUNKS_FILE.open("r", encoding="utf-8") as file:
            chunks = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        print("Could not load knowledge chunks:", exc)
        return []

    if not isinstance(chunks, list):
        print("Knowledge file must contain a JSON list.")
        return []

    return [
        chunk for chunk in chunks
        if isinstance(chunk, dict)
        and isinstance(chunk.get("content"), str)
        and chunk["content"].strip()
        and isinstance(chunk.get("source"), str)
    ]


def retrieve_knowledge(question, chunks, limit=3):
    """Retrieve source chunks using simple keyword matching."""
    stop_words = {
        "the", "is", "a", "an", "of", "to", "and", "in",
        "what", "how", "does", "do", "are", "for", "this",
        "that", "it", "by", "on", "with", "was", "were",
        "can", "could", "would", "should", "me", "tell",
        "about", "from", "which", "used"
    }

    def tokenize(text):
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return {
            word for word in words
            if word not in stop_words and len(word) > 1
        }

    question_words = tokenize(question)

    if not question_words:
        return []

    results = []

    for chunk in chunks:
        content = chunk["content"]
        matches = question_words.intersection(tokenize(content))

        if not matches:
            continue

        score = len(matches) / len(question_words)

        results.append({
            "source": chunk["source"],
            "chunk_id": chunk.get("id", "unknown"),
            "score": round(score, 3),
            "content": content
        })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]



def validate_ai_output(raw_output):
    """Parse and validate the AI's JSON response."""
    try:
        data = json.loads(raw_output)
    except (json.JSONDecodeError, TypeError):
        return None, "Response is not valid JSON."

    if not isinstance(data, dict):
        return None, "Response must be a JSON object."

    required_fields = {"answer", "evidence", "limitation"}

    if set(data.keys()) != required_fields:
        return None, "Response has missing or unexpected fields."

    for field in required_fields:
        if not isinstance(data[field], str) or not data[field].strip():
            return None, f"Field '{field}' must be a non-empty string."

    return data, None



def verify_factual_answer(
    question, data, total_revenue, country_revenue, country_count
):
    """Check supported answers against values calculated by Python."""
    q = question.casefold().strip()
    answer = data["answer"].strip().casefold()

    if "how many countries" in q or "number of countries" in q:
        expected = str(country_count)
        if answer != expected:
            return False, f"Expected {expected} countries."

    elif "total revenue" in q:
        expected = f"£{total_revenue:,.2f}".casefold()
        if answer != expected:
            return False, f"Expected total revenue of £{total_revenue:,.2f}."

    elif "highest revenue" in q or "highest-revenue" in q:
        expected = country_revenue.idxmax()
        if answer != expected.casefold():
            return False, f"Expected highest-revenue country: {expected}."

    else:
        return None, "No factual rule is defined for this question."

    return True, "Answer passed the applicable factual check."



def run_assistant():
    """Load retail data and start the interactive assistant."""
    file_path = Path(__file__).parent / "cleaned_sales.csv"

    if not file_path.exists():
        print(f"Dataset not found: {file_path}")
        print("Check that cleaned_sales.csv is in this folder.")
        return

    df = pd.read_csv(file_path, low_memory=False)

    required_columns = {"Revenue", "Country"}
    missing = required_columns - set(df.columns)

    if missing:
        print("Missing dataset columns:", ", ".join(sorted(missing)))
        return

    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
    df = df.dropna(subset=["Revenue", "Country"])

    if df.empty:
        print("No usable sales records were found.")
        return

    total_revenue = df["Revenue"].sum()
    country_revenue = df.groupby("Country")["Revenue"].sum()
    top_countries = country_revenue.nlargest(5)

    summary = (
        f"Total revenue: £{total_revenue:,.2f}\n"
        f"Number of countries: {df['Country'].nunique()}\n"
        f"Top five countries by revenue:\n{top_countries.to_string()}\n"
    )

    print("\n=== VERIFIED PYTHON CALCULATIONS ===")
    print(f"Total revenue: £{total_revenue:,.2f}")
    print(f"Highest-revenue country: {country_revenue.idxmax()}")
    print(f"Highest country revenue: £{country_revenue.max():,.2f}")
    print(f"Number of countries: {df['Country'].nunique()}")

    print("\n=== RETAIL INTELLIGENCE AI ASSISTANT ===")
    print(summary)
    print("Commands: /history, /reset, /exit")

    history = []
    knowledge_chunks = load_knowledge_chunks()
    print(f"Knowledge chunks loaded: {len(knowledge_chunks)}")

    system_prompt = f"""
You are a retail business analysis assistant.

Use only the verified retail data below.
Do not invent figures. If information is insufficient,
explain this in the limitation field.


Return only a JSON object with exactly three non-empty string fields:
- answer: the direct answer
- evidence: supporting information from the supplied data
- limitation: explain uncertainty or missing information. If there is
  none, write "No material limitation identified."

Never leave any field empty. Do not omit a field.
Do not add Markdown fences or text outside the JSON object.


Verified retail data:
{summary}
"""

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        if question == "/exit":
            print("Goodbye!")
            break

        if question == "/history":
            if not history:
                print("No conversation history yet.")
            else:
                print("\n=== CONVERSATION HISTORY ===")
                for item in history:
                    print(f"\nYou: {item['question']}")
                    print("Assistant:", json.dumps(
                        item["response"], ensure_ascii=False
                    ))
            continue

        if question == "/reset":
            history.clear()
            print("Conversation history cleared. Retail summary is still available.")
            continue

        
        # Retrieve relevant source documents for this question
       
        # Retrieve relevant source documents for this question
        retrieved = retrieve_knowledge(
            question, knowledge_chunks, limit=3
        )

        # Stop if the search finds no matching evidence
        if not retrieved:
            print(
                "\nNo supporting evidence was found "
                "in the available documents."
            )
            print(
                "Consult an appropriate source before "
                "relying on an answer."
            )
            continue

        # Build evidence text before using it in the prompt
        evidence_text = "\n\n".join(
            f"Source: {item['source']}\n"
            f"Chunk ID: {item['chunk_id']}\n"
            f"Content: {item['content']}"
            for item in retrieved
        )

        prompt = (
            system_prompt
            + "\n\nDOCUMENT EVIDENCE:\n"
            + evidence_text
            + "\n\nUse document evidence only for claims about the documentation. "
            + "Do not claim a source supports something it does not say. "
            + "If the documents do not contain sufficient evidence, say so "
            + "in the limitation field. Include the source filename in evidence. "
            + "\nPrevious conversation:\n"
            + json.dumps(history, ensure_ascii=False)
            + f"\nUser question: {question}\n"
            
            + "The evidence field is mandatory and must never be empty. "
            + "For every answer, quote or summarize relevant text from "
            + "the retrieved document and include its source filename "
            + "and chunk ID. If the evidence does not support an answer, "
            + "explain that limitation clearly. "
            + "Return valid JSON with exactly three non-empty string "
            + "fields: answer, evidence, limitation. "
            + "Return the required JSON object."

        )



        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen3:1.7b",
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                },
                timeout=180,
            )
            response.raise_for_status()
            raw_output = response.json().get("response", "")

        except requests.RequestException as exc:
            print("Could not connect to Ollama.")
            print("Check that Ollama is running. Details:", exc)
            continue

        
        result, error = validate_ai_output(raw_output)

        if error:
            print("Structured output validation failed:", error)
            print("Using a source-based fallback response.")

            # Use retrieved source text instead of an invalid AI answer
            source_names = sorted({
                item["source"] for item in retrieved
            })

            evidence = "\n\n".join(
                f"Source: {item['source']}; "
                f"Chunk ID: {item['chunk_id']}\n"
                f"{item['content']}"
                for item in retrieved
            )

            result = {
                "answer": (
                    "The retrieved documents contain information "
                    "relevant to your question. Please review the "
                    "source excerpts below."
                ),
                "evidence": evidence,
                "limitation": (
                    "The AI response was invalid. This fallback "
                    "shows retrieved source text and does not claim "
                    "that the question has been fully answered. "
                    "Sources: " + ", ".join(source_names)
                )
            }

        
        verified, verification_message = verify_factual_answer(
            question,
            result,
            total_revenue,
            country_revenue,
            df["Country"].nunique(),
        )

        if verified is False:
            print("Factual verification failed:", verification_message)
            print("The response was not added to history.")
            continue

        if verified is None:
            print("Factual verification:", verification_message)
        else:
            print("Factual verification:", verification_message)


        print("\n=== AI STRUCTURED RESPONSE ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        history.append({
            "question": question,
            "response": result,
        })


if __name__ == "__main__":
    if "--test-validation" in sys.argv:
        run_validation_tests()
    else:
        run_assistant()
