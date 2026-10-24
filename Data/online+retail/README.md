# Retail Intelligence Assistant

## 1. Project Overview

The Retail Intelligence Assistant is a Python-based application that helps users analyse retail sales data and retrieve relevant information from project knowledge documents.

## 2. Problem and Proposed Solution

Retail datasets can be large and difficult to analyse manually. This application combines deterministic Python data analysis with a language model and retrieval-based knowledge search to help users ask questions in natural language.

## 3. Architecture and Project Structure

The project separates the retail assistant, data analysis tools, knowledge retrieval components, and documentation.

```text
SPECIAL EXAMS/
├── .venv/
├── Data/
│   ├── online+retail/
│   │   ├── agentic_assistant.py
│   │   ├── retail_tools.py
│   │   ├── cleaned_sales.csv
│   │   ├── Online Retail.xlsx
│   │   ├── test_question11.py
│   │   ├── test_retail_tools.py
│   │   └── test_factual_validation.py
│   ├── knowledge/
│   │   ├── build_rag_index.py
│   │   ├── search_rag.py
│   │   ├── processed_chunks.json
│   │   ├── chroma_db/
│   │   └── test_document_processing.py
│   └── prompt_experiments.py
├── tests/                 # Reserved for future centralized tests
├── requirements.txt
└── README.md
```

The interactive assistant uses Ollama for language-model responses, `retail_tools.py` for retail analysis and knowledge retrieval, and ChromaDB for vector-based document search. Existing scripts and data remain in their current locations because some code uses paths relative to those locations.

## 4. Technology Choices

- Python for application logic.
- pandas for structured data analysis.
- Ollama for local language-model inference.
- Retrieval and embeddings for searching project knowledge.
- Python `unittest` for automated testing.

## 5. Installation and Configuration

Create and activate a Python virtual environment, install the project's dependencies, and ensure Ollama is installed and running with the required model available.

The exact dependency installation and model commands should be documented after checking the project's existing configuration.

## 6. Running Locally

### Prerequisites
- Python installed.
- Ollama installed and running.
- The required chat and embedding models available.
- The cleaned retail dataset and knowledge index available in their expected locations.

### Installation

From the project root, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

### Start the assistant

Navigate to the application folder:

```powershell
cd "Data\online+retail"
```

Start the assistant:

```powershell
python agentic_assistant.py
```

Enter a question at the `You:` prompt. Type `exit` to quit.

### Run reliability tests

From `Data\online+retail`, run:

```powershell
python -m unittest test_question11.py -v
```

The latest verified run passed all 12 tests.

### Verified example

Question: `What is the total revenue?`

- Selected tool: `analyze_retail_data`
- Total revenue: £10,666,684.54
- Rows used: 531,283
- Source: `cleaned_sales.csv`

## 7. RAG Design

The knowledge folder contains document-ingestion, indexing, and search components. Retrieval is used to find relevant supporting information for questions that require project knowledge.

## 8. Tool Design

The assistant has two approved tools:

- `analyze_retail_data` for deterministic retail-data calculations.
- `search_retail_knowledge` for retrieving relevant project knowledge.

Tool selection is restricted to approved tool names.

## 9. Evaluation

The project includes automated tests for tool selection, invalid tool responses, connection failure, tool errors, missing data, and missing knowledge evidence.

The Question 11 evaluation report records the test results and known limitations.

## 10. Testing

The project includes automated reliability tests and additional checks for retail tools, factual validation, and document processing.

To run the Question 11 reliability suite, activate the virtual environment from the project root and run:

```powershell
cd "Data\online+retail"
python -m unittest test_question11.py -v
```

The verified test run passed all 12 tests. The suite covers empty input, unavailable data, Ollama connection failures, malformed model responses, unapproved tools, and missing knowledge evidence.

Other test scripts are kept alongside the components they depend on because they use paths relative to their current locations.

## 11. Known Limitations

- The application depends on the local Ollama service and configured model.
- Answers requiring unavailable or irrelevant source documents may lack sufficient evidence.
- Additional end-to-end tests are needed for scenarios not covered by the current automated suite.

## 12. Future Improvements

- Improve logging and configuration management.
- Expand integration and end-to-end tests.
- Document reproducible setup and execution commands.
- Improve handling and reporting of retrieval and model failures.
