"""Retail Intelligence AI Assistant: LLM tool selection with safe, allowlisted tools."""
from __future__ import annotations

import json
import requests
from retail_tools import analyze_retail_data, search_retail_knowledge

import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen3:1.7b")

TOOLS = {
    "analyze_retail_data": analyze_retail_data,
    "search_retail_knowledge": search_retail_knowledge,
}

GENERAL_RESPONSE = (
    "Hello! I can help you analyze retail sales data, calculate total revenue, "
    "identify the country with the highest revenue, count countries, and answer "
    "questions using the project's knowledge documents."
)



def is_general_question(question: str) -> bool:
    text = " ".join(question.casefold().strip().split())

    exact_greetings = {
        "hello",
        "hi",
        "hey",
        "hello there",
        "hi there",
        "good morning",
        "good afternoon",
        "good evening",
        "what can you help me with",
        "what can you do",
        "what are your capabilities",
        "what do you do",
    }

    return text in exact_greetings




def select_tool(question: str) -> str:
    """Select only an approved tool and handle malformed model responses."""
    if is_general_question(question):
        return "general_response"

    prompt = (
        "Choose exactly one tool for the user's question. Return only a JSON object "
        'with key "tool". Allowed tools: "analyze_retail_data", '
        '"search_retail_knowledge". '
        "Use analyze_retail_data for numerical calculations and sales trends. "
        "Use search_retail_knowledge for questions about the dataset and project "
        "documents. If uncertain, choose search_retail_knowledge. "
        "Never invent tool names.\n"
        f"Question: {question}"
    )

    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": CHAT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0, "think": False},
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()

    except requests.RequestException:
        # Let main() display the connection or HTTP error.
        raise
    except (ValueError, TypeError):
        print("Warning: Ollama returned an invalid response.")
        return "search_retail_knowledge"

    message = payload.get("message", {})
    raw = message.get("content", "") if isinstance(message, dict) else ""

    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        print("Warning: Invalid tool-selection JSON; using the safe fallback.")
        return "search_retail_knowledge"

    if not isinstance(parsed, dict):
        print("Warning: Tool selection was not a JSON object.")
        return "search_retail_knowledge"

    tool_name = parsed.get("tool")

    if tool_name not in TOOLS:
        print("Warning: Unapproved tool selection; using the safe fallback.")
        return "search_retail_knowledge"

    return tool_name


def execute_tool(tool_name: str, question: str) -> dict:
    """Execute only functions registered in the allowlist."""
    if tool_name not in TOOLS:
        raise ValueError(f"Tool is not allowed: {tool_name}")
    return TOOLS[tool_name](question)


def format_tool_result(tool_name: str, result: dict) -> None:
    if not result.get("success"):
        print("The tool could not complete the request:", result.get("error", "Unknown error"))
        return

    if tool_name == "analyze_retail_data":
        data = result.get("result", {})
        
        if "total_revenue" in data:
            print(f"Total revenue: £{data['total_revenue']:,.2f}")
        elif "highest_revenue_country" in data:
            print(f"Highest-revenue country: {data['highest_revenue_country']}")
            print(f"Revenue: £{data.get('revenue', 0):,.2f}")
        elif "number_of_countries" in data:
            print(f"Number of countries: {data['number_of_countries']}")
        elif "mean_revenue_per_row" in data:
            print(f"Mean revenue per row: £{data['mean_revenue_per_row']:,.2f}")
        elif "median_revenue_per_row" in data:
            print(f"Median revenue per row: £{data['median_revenue_per_row']:,.2f}")
        elif "maximum_revenue_per_row" in data:
            print(f"Maximum revenue per row: £{data['maximum_revenue_per_row']:,.2f}")
        elif "minimum_revenue_per_row" in data:
            print(f"Minimum revenue per row: £{data['minimum_revenue_per_row']:,.2f}")
        elif "monthly_revenue" in data:
            print("Monthly revenue trend:")
            for month, revenue in data["monthly_revenue"].items():
                print(f"  {month}: £{revenue:,.2f}")
        else:
            print(data.get("message", "This analysis is not supported yet."))

        if "rows_used" in result:
            print(f"Rows used: {result['rows_used']}")
        print("Source: cleaned_sales.csv")
        return

    if tool_name == "search_retail_knowledge":
        if not result.get("evidence_found"):
            print(result.get("message", "I cannot answer from the available project documents because no sufficiently relevant evidence was found."))
            print("Sources: None")
            return

        evidence_results = result.get("results", [])
        context_parts = []
        for item in evidence_results:
            content = item.get("content", "")
            source = item.get("source", "unknown source")
            if content:
                context_parts.append(f"Source: {source}\nEvidence: {content}")
        if not context_parts:
            print("Relevant documents were retrieved, but no readable evidence text was returned.")
            return

        prompt = (
            "Answer the user's question using only the project evidence below. Be concise. "
            "Do not use outside knowledge. If the evidence does not answer the question, say so.\n\n"
            f"Question: {CURRENT_QUESTION}\n\nEvidence:\n" + "\n\n".join(context_parts)
        )
        
        print("\nAnswer:", flush=True)
        try:
            with requests.post(
                OLLAMA_CHAT_URL,
                json={
                    "model": CHAT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                    "options": {"temperature": 0, "think": False},
                },
                timeout=120,
                stream=True,
            ) as response:
                response.raise_for_status()
                received_text = False

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    chunk = json.loads(line)
                    message = chunk.get("message", {})
                    content = message.get("content", "")

                    if content:
                        print(content, end="", flush=True)
                        received_text = True

                if not received_text:
                    print("I could not generate an answer from the retrieved evidence.")
                else:
                    print()
        except (requests.RequestException, json.JSONDecodeError) as error:
            print(f"\nStreaming response failed: {error}")
            return

        sources = result.get("sources") or list(dict.fromkeys(item.get("source", "unknown") for item in evidence_results))
        print("\nRetrieved source filenames:")
        for source in sources:
            print(f"- {source}")


CURRENT_QUESTION = ""


def main() -> None:
    global CURRENT_QUESTION
    print("=" * 55)
    print("RETAIL INTELLIGENCE - TOOL-USE ASSISTANT")
    print(f"Model: {CHAT_MODEL}")
    print("=" * 55)
    print("Ask a retail question. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            print("Please enter a question.\n")
            continue

        if is_general_question(question):
            print(f"\n{GENERAL_RESPONSE}\n")
            continue

        CURRENT_QUESTION = question
        try:
            tool_name = select_tool(question)
            if tool_name == "general_response":
                print(f"\n{GENERAL_RESPONSE}\n")
                continue
            print(f"\nSelected tool: {tool_name}")
            result = execute_tool(tool_name, question)
            format_tool_result(tool_name, result)
            print()
        except requests.RequestException as error:
            print(f"\nConnection error: Could not reach Ollama. Make sure Ollama is running. Details: {error}\n")
        except (ValueError, KeyError, TypeError) as error:
            print(f"\nTool workflow error: {error}\n")
        except Exception as error:
            print(f"\nUnexpected error: {error}\n")


if __name__ == "__main__":
    main()
