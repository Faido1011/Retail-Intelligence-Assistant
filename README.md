# Retail Intelligence Assistant

## 1. Project Overview

The Retail Intelligence Assistant is a Python application that answers questions about retail sales data using deterministic Python analysis and a local language model. The project also includes a retrieval-augmented generation (RAG) component for searching project knowledge documents.

## 2. Problem and Proposed Solution

Retail datasets can be large and difficult to analyse manually. This project combines data processing, allowlisted tools, a local language model, and document retrieval to help users explore sales information and obtain evidence-based answers.

## 3. Project Structure

- `Data/online+retail/` — retail assistant, analysis tools, datasets, tests, reports, and screenshots.
- `Data/knowledge/` — document processing, RAG scripts, knowledge documents, and processed chunks.
- `Data/prompt_experiments.py` — prompt experimentation.
- `tests/` — reserved for future centralized tests.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — builds the assistant's Python image.
- `docker-compose.yml` — configures the container.
- `.env.example` — example configuration variables.

## 4. Technologies

- Python 3.11
- pandas
- Requests
- Ollama
- ChromaDB
- Docker and Docker Compose
- Python `unittest`

## 5. Prerequisites

For local execution or Docker execution, install Python and Ollama, and ensure the required Ollama model is available.

The interactive assistant uses `qwen3:1.7b`. The RAG index-building script uses `embeddinggemma:latest`.

## 6. Install and Run Locally

From the project root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Ensure Ollama is running and the required model is available. Then run:

```powershell
Set-Location "Data\online+retail"
python agentic_assistant.py
```

Enter a retail question at the `You:` prompt. Type `exit` to quit.

## 7. Run Reliability Tests

From the project root:

```powershell
Set-Location "Data\online+retail"
python -m unittest test_question11.py -v
```

The latest recorded test run passed all 12 tests.

## 8. Run with Docker

Ensure Docker Desktop is running and Ollama is running on the host computer.

Build the image:

```powershell
docker compose build
```

Start an interactive assistant session:

```powershell
docker compose run --rm retail-assistant
```

Ask a question such as `What is the total revenue?`. Type `exit` to quit.

The container connects to Ollama through `host.docker.internal` and uses the existing `cleaned_sales.csv` file as a read-only mount.

The Docker build and an interactive retail-analysis request have been tested successfully.

## 9. RAG Design

The knowledge component processes source documents into chunks and stores the chunks in `processed_chunks.json`. The index builder generates embeddings through Ollama and stores them in ChromaDB.

To rebuild the index, ensure Ollama is running with `embeddinggemma:latest`, then run the index-building script from the project root:

```powershell
python "Data\knowledge\build_rag_index.py"
```

The generated `Data/knowledge/chroma_db/` directory is excluded from Git. Rebuild it when needed.

## 10. Tool Design

The interactive assistant uses approved tools:

- `analyze_retail_data` — performs deterministic calculations on the retail dataset.
- `search_retail_knowledge` — retrieves relevant project knowledge.

Tool selection is restricted to approved tool names, and the reliability tests cover invalid model responses and tool failures.

## 11. Evaluation

The Question 11 reliability suite contains 12 tests. The latest recorded run passed all 12 tests, including checks for missing data, Ollama connection failures, malformed model responses, and invalid tool selections.

The interactive Docker test returned total revenue of £10,666,684.54 using 531,283 rows from `cleaned_sales.csv`.

RAG indexing and retrieval have not yet been verified inside Docker.

## 12. Limitations

- The assistant depends on a running local Ollama service.
- Answers depend on the dataset and available knowledge documents.
- The RAG index may need to be rebuilt if it is unavailable.
- Local model performance depends on available computer resources.
- Additional end-to-end and containerized RAG tests are needed.

## 13. Future Improvements

- Expand integration and end-to-end testing.
- Improve logging and centralized configuration.
- Improve retrieval evaluation and error reporting.
- Expand configuration options and deployment documentation.