
from pathlib import Path
import requests
import pandas as pd

# Locate the cleaned retail dataset
file_path = Path(__file__).parent / "cleaned_sales.csv"

if not file_path.exists():
    print("Dataset not found. Run main.py first.")
    raise SystemExit(1)

df = pd.read_csv(file_path)

# Calculate reliable business figures using Python
total_revenue = df["Revenue"].sum()
print("\n=== VERIFIED PYTHON CALCULATIONS ===")

print("Total revenue: £", round(df["Revenue"].sum(), 2))

country_revenue = df.groupby("Country")["Revenue"].sum()

print("Country with highest revenue:", country_revenue.idxmax())
print("Highest country revenue: £", round(country_revenue.max(), 2))

print("Number of countries:", df["Country"].nunique())
top_five_revenue = (
    df.groupby("Country")["Revenue"]
    .sum()
    .nlargest(5)
    .sum()
)

print("Total revenue: £", round(total_revenue, 2))
print("Top 5 countries combined: £", round(top_five_revenue, 2))
top_countries = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

summary = f"""
Retail sales summary:
Total revenue: £{total_revenue:,.2f}

Top 5 countries by revenue:
{top_countries.to_string()}
"""

print("=== RETAIL INTELLIGENCE AI ASSISTANT ===")
print(summary)
print("\nAsk a question about these sales figures.")
print("Type 'exit' to quit.")

while True:
    question = input("\nYou: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        print("Please enter a question.")
        continue

    prompt = f"""
You are a retail business analysis assistant.
Answer using the sales information provided below.
Do not invent figures that are not in the information.
If the information is insufficient, say so.
Explain your answer in simple English.

{summary}

User question: {question}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:1.7b",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()
        answer = response.json()["response"]

        print("\nAI:", answer)

    except requests.exceptions.ConnectionError:
        print(
            "Cannot connect to Ollama. "
            "Open Ollama and try again."
        )
    except requests.exceptions.Timeout:
        print("Ollama took too long to respond. Please try again.")
    except requests.exceptions.RequestException as error:
        print("Request error:", error)
    except (KeyError, ValueError):
        print("Could not read Ollama's response.")
