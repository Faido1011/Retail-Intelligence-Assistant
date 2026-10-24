
import json
from pathlib import Path

folder = Path(__file__).parent
json_file = folder / "processed_chunks.json"

with json_file.open("r", encoding="utf-8") as file:
    chunks = json.load(file)

print("DOCUMENT PROCESSING TEST")
print("-" * 35)

assert len(chunks) > 0, "FAIL: No chunks were created."

for chunk in chunks:
    assert chunk["id"], "FAIL: Missing chunk ID."
    assert chunk["source"], "FAIL: Missing source filename."
    assert chunk["content"].strip(), "FAIL: Empty chunk content."
    assert chunk["chunk_index"] >= 1, "FAIL: Invalid chunk index."
    assert chunk["total_chunks"] >= 1, "FAIL: Invalid total chunks."

print("PASS: Chunks exist.")
print("PASS: Metadata fields are present.")
print("PASS: No empty chunks were found.")
print(f"PASS: {len(chunks)} chunks verified.")

combined_text = " ".join(chunk["content"] for chunk in chunks)

if "Evidence policy" in combined_text:
    print("PASS: Evidence policy text was retained.")
else:
    print("WARNING: Evidence policy text was not found.")
