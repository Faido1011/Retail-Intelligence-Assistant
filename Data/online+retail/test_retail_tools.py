
from retail_tools import (
    analyze_retail_data,
    search_retail_knowledge,
)


def show_result(title, result):
    print(f"\n{'=' * 55}")
    print(title)
    print("=" * 55)

    for key, value in result.items():
        print(f"{key}: {value}")


def main():
    # Test Tool 1: Deterministic data analysis
    result1 = analyze_retail_data("What is the total revenue?")
    show_result("TEST 1: TOTAL REVENUE", result1)

    # Test Tool 2: Search the knowledge base
    result2 = search_retail_knowledge(
        "What is the purpose of the retail dataset?"
    )
    show_result("TEST 2: KNOWLEDGE SEARCH", result2)

    # Test missing-evidence handling
    result3 = search_retail_knowledge(
        "What is the capital of Japan?"
    )
    show_result("TEST 3: UNSUPPORTED KNOWLEDGE QUESTION", result3)


if __name__ == "__main__":
    main()
