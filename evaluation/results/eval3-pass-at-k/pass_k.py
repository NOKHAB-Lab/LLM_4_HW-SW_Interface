import json
import pandas as pd
from collections import defaultdict

# Ask the user to enter the JSON filename
input_file = input("Enter the JSON filename (e.g., input.json): ").strip()

# Load JSON data
with open(input_file, "r") as f:
    data = json.load(f)

# Prepare structure to group data by ID
grouped = defaultdict(lambda: {
    "category": "",
    "base_statuses": {},
    "finetuned_statuses": {}
})

# Populate the grouped dictionary
for item in data:
    example_id = item["id"]
    sub_id = int(item["subid"])

    grouped[example_id]["category"] = item["category"]
    grouped[example_id]["base_statuses"][sub_id] = item.get("base_all_test_cases_execution_status", False)
    grouped[example_id]["finetuned_statuses"][sub_id] = item.get("finetuned_all_test_cases_execution_status", False)

# Generate the output rows
rows = []
for example_id, info in grouped.items():
    row = {
        "category": info["category"],
        "base_pass@1": int(info["base_statuses"].get(0, False)),
        "finetuned_pass@1": int(info["finetuned_statuses"].get(0, False)),
        "base_pass@3": int(any(info["base_statuses"].get(i, False) for i in range(3))),
        "finetuned_pass@3": int(any(info["finetuned_statuses"].get(i, False) for i in range(3))),
        "base_pass@5": int(any(info["base_statuses"].get(i, False) for i in range(5))),
        "finetuned_pass@5": int(any(info["finetuned_statuses"].get(i, False) for i in range(5))),
    }
    rows.append(row)

# Save to CSV
df = pd.DataFrame(rows)
df.to_csv("evaluation_pass_summary.csv", index=False)
print("Saved to evaluation_pass_summary.csv")
