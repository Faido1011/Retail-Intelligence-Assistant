
import json
import sys
from pathlib import Path

import pandas as pd
import requests


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

        prompt = (
            system_prompt
            + "\nPrevious conversation:\n"
            + json.dumps(history, ensure_ascii=False)
            + f"\nUser question: {question}\n"
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
            print("The invalid response was not added to history.")
            continue

        
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
