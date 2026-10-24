# Question 3: LLM Integration and Prompt Engineering

## Objective
To integrate a locally running Large Language Model (LLM) into the Retail Intelligence AI Assistant and compare different prompting strategies.

## Model and Tools
- **LLM:** Qwen3 1.7B
- **Runtime:** Ollama
- **Programming language:** Python
- **Integration library:** Ollama Python library

## Experimental Setup
Three prompt styles were tested using the same retail sales data and the same question: identify the country with the highest revenue.

### Prompt A: Basic
A general instruction asking the model to answer the retail sales question.

**Observed result:** The model identified the United Kingdom as the highest-revenue country, reporting £9,025,222.08, and provided a detailed explanation.

### Prompt B: Domain-specific
The model was assigned the role of a retail sales analyst and instructed to use only the supplied figures, avoid inventing numbers, and use simple English.

**Observed result:** The model correctly identified the United Kingdom and its revenue in a concise response.

### Prompt C: Structured and cautious
The model was instructed to use only the supplied evidence and organize the response under Finding, Evidence, and Limitation.

**Observed result:** The model correctly identified the United Kingdom and followed the requested three-heading structure.

## Comparison and Discussion
All three prompts produced the correct answer for the supplied data. Prompt A generated a longer explanation, Prompt B produced a concise answer, and Prompt C followed a predefined structure and acknowledged limitations.

The experiment demonstrates that prompt design affects the style, length, and organization of LLM responses. Further testing with more questions is required before drawing conclusions about comparative accuracy.

## Conclusion
The Retail Intelligence AI Assistant successfully integrated Qwen3 1.7B through Ollama. The experiment demonstrated three prompting strategies and showed that structured instructions can guide the model toward a more predictable response format.