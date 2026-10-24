# Question 5: Structured Outputs and Validation

## 1. Objective
The objective was to make the Retail Intelligence AI Assistant return structured, predictable responses and validate the output before using it.

## 2. Implementation
The system uses the local Qwen3 1.7B model through the Ollama API. The request specifies JSON output using `"format": "json"`.

Each response must contain exactly three string fields:

- `answer`: The direct answer to the user's question.
- `evidence`: Supporting information from the retail sales summary.
- `limitation`: Any uncertainty or missing information.

The Python function `validate_ai_output()` parses the response using `json.loads()` and checks the JSON type, required field names, and non-empty string values.

## 3. Error Handling
If the response is invalid JSON or does not match the expected structure, the program reports a validation error and does not store the invalid response in conversation history. The application also handles API connection errors, timeouts, and request failures.

## 4. Testing and Results
The application was tested with the questions "Which country has the highest revenue?" and "What evidence supports your answer?"

The model returned structured JSON responses. The `/history` command displayed previous questions and answers, while `/reset` cleared the conversation history.

Python independently calculated total revenue of £10,666,684.54 and identified the United Kingdom as the highest-revenue country, with revenue of £9,025,222.08.

## 5. Limitations
Structural validation does not guarantee that the model's claims are factually correct. The system should compare numerical claims against verified Python calculations. Conversation history is stored temporarily in memory and is cleared when the application is reset or restarted.

## 6. Conclusion
The implementation demonstrates structured JSON generation, schema-like validation, and error handling. It improves the consistency of AI responses while recognizing that independent verification is still necessary.
