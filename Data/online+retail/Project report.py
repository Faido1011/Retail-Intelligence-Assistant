# Question 5: Structured Outputs and Validation

## 1. Introduction

The Retail Intelligence AI Assistant uses a Large Language Model (LLM) to answer questions about sales data. To improve the reliability and consistency of its responses, the system implements structured JSON output, response validation, error handling, and factual verification using Python-calculated values.

## 2. Schema Definition

The assistant requires every response to contain exactly three non-empty string fields:

- **answer:** Provides the direct answer to the user's question.
- **evidence:** Provides supporting information from the retail dataset.
- **limitation:** Identifies uncertainty or missing information, or states when no material limitation has been identified.

The system uses Python's built-in `json` module to parse the response and validate the required structure and field types.

## 3. Structured Output Generation

The system uses the local Ollama model `qwen3:1.7b` to generate responses. The request specifies JSON output format, and the prompt instructs the model to return the three required fields without additional text.

Example of a valid structured response:

```json
{
  "answer": "38",
  "evidence": "Number of countries: 38",
  "limitation": "No material limitation identified."
}
```

## 4. Response Validation and Error Handling

The `validate_ai_output()` function checks whether the response:

1. Contains valid JSON.
2. Is a JSON object.
3. Contains exactly the three required fields.
4. Provides a non-empty string for every field.

If a response fails any of these checks, the system displays a validation error and does not add the invalid response to the conversation history.

The validation tests cover valid JSON, malformed JSON, missing fields, incorrect data types, and empty answers.

## 5. Factual Verification

In addition to structural validation, the system implements a `verify_factual_answer()` function. This function compares selected answers against values independently calculated from the retail dataset using Python and pandas.

The implemented checks cover three question types:

- Highest-revenue country.
- Total revenue.
- Number of countries represented in the dataset.

The verified results are:

| Measure | Verified result |
|---|---:|
| Total revenue | £10,666,684.54 |
| Highest-revenue country | United Kingdom |
| Highest country revenue | £9,025,222.08 |
| Number of countries | 38 |

The factual verification function rejects an answer when it does not match the expected result for a supported question type. Questions outside the implemented rules are reported as not covered by a factual verification rule.

## 6. Testing and Results

The system was tested using both valid and invalid responses.

| Test case | Expected behavior | Result |
|---|---|---|
| Valid JSON response | Accept | Passed |
| Malformed JSON | Reject | Passed |
| Missing required field | Reject | Passed |
| Incorrect data type | Reject | Passed |
| Empty answer field | Reject | Passed |
| Highest-revenue country | Verify United Kingdom | Passed |
| Total revenue | Verify £10,666,684.54 | Passed |
| Number of countries | Verify 38 | Passed |
| Deliberately incorrect highest-revenue answer, “France” | Reject and identify United Kingdom as expected | Passed |

The negative factual-verification test confirmed that the function rejected “France” and returned the expected country, “United Kingdom.”

## 7. Limitations

The current implementation has several limitations:

- Factual verification supports only three specific question types.
- Structural validation does not prove that every statement in the evidence or limitation fields is true.
- The system does not yet implement an automatic retry when a response fails validation.
- The factual verification function checks selected answer values rather than validating all numerical claims in the response.

These limitations should be considered when interpreting the assistant's output.

## 8. Conclusion

The implementation demonstrates how structured output and validation can improve the reliability of an LLM-powered data analysis application. By combining JSON validation with independent Python calculations, the system can reject malformed responses and detect incorrect answers for supported question types. This reduces reliance on unverified model-generated values and provides a foundation for extending factual verification to additional retail analysis questions.