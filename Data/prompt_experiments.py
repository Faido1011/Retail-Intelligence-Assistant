
from ollama import chat

MODEL = "qwen3:1.7b"

# The same business question will be used for all three experiments.
QUESTION = (
    "Using the sales figures provided, identify the country "
    "with the highest revenue and explain the result."
)

SALES_CONTEXT = """
Retail sales data:
United Kingdom: £9,025,222.08
Netherlands: £285,446.34
EIRE: £283,453.96
Germany: £228,867.14
France: £209,715.11

These are revenue figures from the preliminary sales analysis.
"""

# Three prompt variations to compare fairly.
PROMPTS = {
    "Prompt A - Basic": (
        "Answer the user's question about retail sales."
    ),

    "Prompt B - Domain-specific": (
        "You are a retail sales analyst. Answer using only "
        "the supplied sales figures. Do not invent numbers. "
        "Use simple English and identify the highest-revenue country."
    ),

    "Prompt C - Structured and cautious": (
        "You are a careful retail sales analyst. Use only the "
        "provided evidence. Identify the country with the highest "
        "revenue and quote its exact revenue. If evidence is missing, "
        "say so. Respond with these headings: Finding, Evidence, "
        "Limitation. Do not calculate totals that were not requested."
    ),
}





def run_experiment(name, system_prompt):
    print("\n" + "=" * 65)
    print(name)
    print("=" * 65)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": SALES_CONTEXT + "\nQuestion: " + QUESTION
        },
    ]

    try:
        response = chat(
            model=MODEL,
            messages=messages,
            options={
                "temperature": 0.2,
                "num_predict": 300
            },
            think=False,
            stream=False
        )

        answer = response.message.content
        print("AI ANSWER:")
        print(answer if answer else "No answer returned.")

    except Exception as error:
        print("Experiment failed:", error)

if __name__ == "__main__":
    for name, prompt in PROMPTS.items():
        run_experiment(name, prompt)
