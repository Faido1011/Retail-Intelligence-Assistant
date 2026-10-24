
import importlib.util
from pathlib import Path

import pandas as pd

# Load the factual verification function from your assistant.
assistant_path = Path(__file__).parent / "ai_assistant_q5.py"

spec = importlib.util.spec_from_file_location(
    "q5_assistant", assistant_path
)
assistant = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assistant)

# Use verified values for this test.
country_revenue = pd.Series({
    "United Kingdom": 9025222.084,
    "France": 209715.110,
})

incorrect_response = {
    "answer": "France",
    "evidence": "France generated the highest revenue.",
    "limitation": "Test of an incorrect answer.",
}

passed, message = assistant.verify_factual_answer(
    "Which country generated the highest revenue?",
    incorrect_response,
    10666684.54,
    country_revenue,
    38,
)

print("Test answer:", incorrect_response["answer"])
print("Verification result:", passed)
print("Message:", message)

if passed is False:
    print("PASS: The incorrect answer was rejected.")
else:
    print("FAIL: The incorrect answer was not rejected.")
