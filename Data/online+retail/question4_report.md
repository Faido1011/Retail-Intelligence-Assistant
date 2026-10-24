# Question 4: Conversation and Application State

## 1. Objective

The objective is to implement multi-turn conversation memory in the Retail Intelligence AI Assistant, allowing users to ask follow-up questions and manage conversation history.

## 2. Implementation

The application maintains a Python list called `messages` containing system instructions, user questions, and AI responses.

The conversation history is included in the prompt sent to the local Qwen3 1.7B model through Ollama. This allows the model to use previous messages when answering follow-up questions.

The application supports these commands:

- `/history`: Displays previous user questions and AI answers.
- `/reset`: Clears conversation history while retaining the retail sales information.
- `/exit`: Ends the application.

## 3. Testing and Results

| Test | Expected result | Observed result |
|---|---|---|
| Ask which country has the highest revenue | Identify the leading country | Passed: United Kingdom |
| Ask for its revenue in a follow-up question | Use previous context | Passed |
| Run `/history` | Display conversation messages | Passed |
| Run `/reset` | Clear conversation messages | Passed |
| Run `/history` after reset | Show no previous user/assistant messages | Passed |

## 4. Application Memory

Conversation history is stored temporarily in the Python application's memory. It is not saved permanently to a file or database. The history is lost when the application closes.

The retail sales summary remains available after `/reset` because it is maintained separately from the conversation history.

## 5. Limitations and Future Improvements

Future improvements could include saving and loading conversations, validating AI responses, and using Ollama's chat API with structured message history.

## 6. Conclusion

The implemented conversation state supports follow-up questions, history viewing, and resetting the conversation. The tests performed demonstrated that these features work as expected in the tested session.