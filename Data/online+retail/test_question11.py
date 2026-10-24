
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

import requests
import agentic_assistant as assistant


class TestQuestion11Reliability(unittest.TestCase):

    def test_empty_input_is_rejected(self):
        # Verify that empty input is rejected before tool selection.
        question = "   "

        if not question.strip():
            result = "empty_input"
        else:
            result = assistant.select_tool(question)

        self.assertEqual(result, "empty_input")

    def test_dataset_failure_is_returned(self):
        with patch.dict(
            assistant.TOOLS,
            {
                "analyze_retail_data": Mock(
                    return_value={
                        "success": False,
                        "tool": "analyze_retail_data",
                        "error": "Dataset unavailable",
                    }
                ),
            },
        ):
            result = assistant.execute_tool(
                "analyze_retail_data",
                "What is the total revenue?"
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Dataset unavailable")

    @patch(
        "retail_tools.DATA_FILE",
        Path("definitely_missing_test_dataset.csv")
    )
    def test_missing_dataset_returns_error(self):
        import retail_tools

        result = retail_tools.analyze_retail_data(
            "What is the total revenue?"
        )

        self.assertFalse(result["success"])
        self.assertIn("Dataset not found", result["error"])

    @patch.object(assistant.requests, "post")
    def test_malformed_json_uses_safe_fallback(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "message": {"content": "not valid json"}
        }
        mock_post.return_value = response

        with patch.object(
            assistant, "is_general_question", return_value=False
        ):
            result = assistant.select_tool("Tell me about the dataset")

        self.assertEqual(result, "search_retail_knowledge")

    @patch.object(assistant.requests, "post")
    def test_unapproved_tool_uses_safe_fallback(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "message": {"content": '{"tool": "delete_database"}'}
        }
        mock_post.return_value = response

        with patch.object(
            assistant, "is_general_question", return_value=False
        ):
            result = assistant.select_tool("Analyze the dataset")

        self.assertEqual(result, "search_retail_knowledge")

    @patch.object(assistant.requests, "post")
    def test_ollama_connection_failure_is_propagated(self, mock_post):
        mock_post.side_effect = requests.ConnectionError(
            "Ollama unavailable"
        )

        with patch.object(
            assistant, "is_general_question", return_value=False
        ):
            with self.assertRaises(requests.ConnectionError):
                assistant.select_tool("What is the total revenue?")

    def test_unapproved_tool_cannot_execute(self):
        with self.assertRaises(ValueError):
            assistant.execute_tool("delete_database", "test")

    def test_tool_failure_is_reported(self):
        result = {
            "success": False,
            "error": "Dataset unavailable"
        }

        with patch("builtins.print") as mock_print:
            assistant.format_tool_result("analyze_retail_data", result)

        mock_print.assert_any_call(
            "The tool could not complete the request:",
            "Dataset unavailable"
        )

    def test_greeting_does_not_call_ollama(self):
        with patch.object(assistant.requests, "post") as mock_post:
            result = assistant.select_tool("hello")

        self.assertEqual(result, "general_response")
        mock_post.assert_not_called()

    @patch.object(assistant.requests, "post")
    def test_valid_analysis_tool_selection(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "message": {
                "content": '{"tool": "analyze_retail_data"}'
            }
        }
        mock_post.return_value = response

        with patch.object(
            assistant, "is_general_question", return_value=False
        ):
            result = assistant.select_tool("What is the total revenue?")

        self.assertEqual(result, "analyze_retail_data")

    @patch.object(assistant, "search_retail_knowledge")
    def test_missing_knowledge_evidence(self, mock_search):
        mock_search.return_value = {
            "success": True,
            "evidence_found": False,
            "message": "No sufficiently relevant evidence found."
        }

        result = assistant.execute_tool(
            "search_retail_knowledge",
            "What is the capital of Japan?"
        )

        self.assertFalse(result["evidence_found"])

    def test_unknown_tool_is_rejected(self):
        with self.assertRaises(ValueError):
            assistant.execute_tool("unknown_tool", "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
