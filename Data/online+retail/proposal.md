# Question 1: Problem Definition and System Proposal

## Project Title
**Retail Intelligence AI Assistant: An LLM-Powered System for Sales Analysis and Knowledge Retrieval**

### 1. Real-World Problem

Retail businesses collect large amounts of sales data, including product descriptions, quantities sold, prices, invoice dates, customers, and countries. However, understanding this information can require data-processing skills and time-consuming manual analysis.

This project addresses the problem of making retail sales information easier to analyze and understand. It uses the UCI Online Retail dataset, which contains 541,909 transaction records.

The proposed system will calculate sales indicators, identify high-performing products and countries, and explain the results in simple English.

### 2. Intended Users

The intended users include:

- Retail business owners who want to understand business performance.
- Sales managers who need to identify products and markets generating revenue.
- Data analysts who want to explore sales data more efficiently.
- Students learning data science and AI application development.

### 3. Why an AI-Based Approach Is Appropriate

A conventional data-analysis program can calculate totals, averages, rankings, and trends accurately. However, users may need programming knowledge to request these calculations or interpret the results.

Integrating a large language model (LLM) through Ollama allows users to ask questions in natural language. The model can explain calculated results and provide evidence-based business suggestions.

Python will perform numerical calculations, while the LLM will interpret questions and explain the results. This design reduces reliance on the model for arithmetic and helps improve reliability.

### 4. Main Application Capabilities

The planned application will provide the following capabilities:

1. Load and preprocess retail sales data from Excel and CSV files.
2. Calculate revenue, transaction counts, product rankings, and country rankings using Python.
3. Answer natural-language questions about sales performance using a local LLM through Ollama.
4. Retrieve relevant information from supporting documents using a Retrieval-Augmented Generation (RAG) pipeline.
5. Generate structured responses and validate them before presenting results.
6. Handle errors such as missing data, unavailable models, and invalid user input.
7. Evaluate answer quality using a collection of representative test cases.

These are planned capabilities; they will be implemented and tested progressively.

### 5. Limitations, Risks, and Human Review

**Risk 1: Incorrect AI-generated explanations.** The LLM may misunderstand a question or produce an unsupported conclusion. Important conclusions must be checked against the underlying data.

**Risk 2: Data quality problems.** Missing customer identifiers, missing descriptions, returned goods, cancelled invoices, and unusual prices may affect the interpretation of results. The application must document its cleaning rules.

**Risk 3: Limited dataset coverage.** The selected dataset covers a particular historical period and may not represent current retail conditions or every business.

**Risk 4: Unsupported business recommendations.** Historical sales patterns do not prove why customers behave in a particular way. Recommendations should be treated as suggestions for human review.

**Risk 5: Model or service failure.** Ollama may be unavailable or take too long to respond. The application must handle such failures gracefully.

### 6. Measurable Success Criteria

The project will use the following criteria to evaluate usefulness and reliability:

- **Numerical accuracy:** At least 95% of tested numerical answers must match independently verified Python calculations, using a test set of at least 20 questions with known expected results.
- **Response reliability:** The application must handle empty questions and simulated model-unavailable situations without crashing.
- **Data analysis:** The application must correctly calculate total revenue and identify the highest-revenue country from the selected dataset.
- **Retrieval quality:** Test whether document-based answers are supported by retrieved source material and whether the system admits when evidence is unavailable.

The evaluation results will be recorded and used to identify areas for improvement.






