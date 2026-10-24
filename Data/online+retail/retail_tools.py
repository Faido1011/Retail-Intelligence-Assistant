
from pathlib import Path

import pandas as pd


# Paths to existing project files
DATA_FILE = Path(__file__).parent / "cleaned_sales.csv"
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def analyze_retail_data(question: str) -> dict:
    """
    Tool 1: Calculate retail statistics using Python and pandas.
    """
    if not DATA_FILE.exists():
        return {
            "success": False,
            "tool": "analyze_retail_data",
            "error": f"Dataset not found: {DATA_FILE.name}",
        }

    try:
        df = pd.read_csv(DATA_FILE, low_memory=False)

        required = {"Revenue", "Country"}
        missing = required - set(df.columns)

        if missing:
            return {
                "success": False,
                "tool": "analyze_retail_data",
                "error": f"Missing columns: {sorted(missing)}",
            }

        df["Revenue"] = pd.to_numeric(
            df["Revenue"], errors="coerce"
        )
        df["Country"] = df["Country"].astype("string").str.strip()

        valid = df.dropna(subset=["Revenue", "Country"])
        valid = valid[valid["Country"] != ""]

        
        q = question.casefold()

        if "how many countries" in q or "number of countries" in q:
            result = {
                "number_of_countries": int(valid["Country"].nunique())
            }

        elif "highest revenue" in q or "top country" in q:
            revenue_by_country = valid.groupby("Country")["Revenue"].sum()
            country = revenue_by_country.idxmax()

            result = {
                "highest_revenue_country": str(country),
                "revenue": round(float(revenue_by_country.max()), 2),
            }

        elif "total revenue" in q:
            result = {
                "total_revenue": round(float(valid["Revenue"].sum()), 2)
            }

        elif "mean revenue" in q or "average revenue" in q:
            result = {
                "mean_revenue_per_row": round(float(valid["Revenue"].mean()), 2)
            }

        elif "median revenue" in q:
            result = {
                "median_revenue_per_row": round(float(valid["Revenue"].median()), 2)
            }

        
        elif "maximum revenue" in q or "max revenue" in q:
            result = {
                "maximum_revenue_per_row": round(float(valid["Revenue"].max()), 2)
            }



        
        elif "minimum revenue" in q or "min revenue" in q:
            result = {
                "minimum_revenue_per_row": round(float(valid["Revenue"].min()), 2)
            }

    

        elif "monthly revenue" in q or "monthly sales trend" in q:
            dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
            monthly_data = pd.DataFrame({
                "InvoiceDate": dates,
                "Revenue": pd.to_numeric(df["Revenue"], errors="coerce"),
            }).dropna()

            monthly_data["Month"] = monthly_data["InvoiceDate"].dt.to_period("M")

            monthly_totals = monthly_data.groupby("Month")["Revenue"].sum()

            result = {
                "monthly_revenue": {
                    str(month): round(float(revenue), 2)
                    for month, revenue in monthly_totals.items()
                }
            }

        else:
            result = {
                "available_analyses": [
                    "total revenue",
                    "highest revenue country",
                    "number of countries",
                    "mean revenue",
                    "median revenue",
                    "maximum revenue",
                    "minimum revenue",
                    "monthly revenue trend",
                ],
                "message": "Please ask for one of the supported analyses.",
            }








        return {












            "success": True,
            "tool": "analyze_retail_data",
            "result": result,
            "rows_used": int(len(valid)),








        }








    except (OSError, ValueError, pd.errors.ParserError) as error:




        return {
            "success": False,
            "tool": "analyze_retail_data",
            "error": str(error),
        }


def search_retail_knowledge(question: str) -> dict:
    """
    Tool 2: Retrieve relevant evidence from the existing RAG index.
    """
    try:
        import sys

        # Allow importing search_rag.py from Data/knowledge.
        knowledge_path = str(KNOWLEDGE_DIR)
        if knowledge_path not in sys.path:
            sys.path.insert(0, knowledge_path)

        from search_rag import search_knowledge

        matches = search_knowledge(question, top_k=3)
        threshold = 0.75

        relevant = [
            item for item in matches
            if item["distance"] <= threshold
        ]

        if not relevant:
            return {
                "success": True,
                "tool": "search_retail_knowledge",
                "evidence_found": False,
                "message": "No sufficiently relevant evidence found.",
                "sources": [],
            }

        return {
            "success": True,
            "tool": "search_retail_knowledge",
            "evidence_found": True,
            "results": [
                {
                    "source": item["source"],
                    "chunk_index": item["chunk_index"],
                    "distance": round(float(item["distance"]), 4),
                    "content": item["content"],
                }
                for item in relevant
            ],
            "sources": sorted({
                item["source"] for item in relevant
            }),
        }

    except Exception as error:
        return {
            "success": False,
            "tool": "search_retail_knowledge",
            "error": str(error),
        }


if __name__ == "__main__":
    print("Retail tools module loaded.")
    print("Available tools:")
    print("1. analyze_retail_data(question)")
    print("2. search_retail_knowledge(question)")
