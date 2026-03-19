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
    base_statuses = info["base_statuses"]
    finetuned_statuses = info["finetuned_statuses"]

    row = {
        "category": info["category"],
        "base_pass@1": int(base_statuses.get(0, False)),
        "finetuned_pass@1": int(finetuned_statuses.get(0, False)),
        "base_pass@3": int(any(base_statuses.get(i, False) for i in range(3))),
        "finetuned_pass@3": int(any(finetuned_statuses.get(i, False) for i in range(3))),
        "base_pass@5": int(any(base_statuses.get(i, False) for i in range(5))),
        "finetuned_pass@5": int(any(finetuned_statuses.get(i, False) for i in range(5))),
    }
    rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv("evaluation_pass_summary.csv", index=False)
print("Saved to evaluation_pass_summary.csv")

# Compute overall averages
metrics = ["base_pass@1", "finetuned_pass@1", "base_pass@3", "finetuned_pass@3", "base_pass@5", "finetuned_pass@5"]
averages = {metric: df[metric].mean() for metric in metrics}

print("\nOverall Averages:")
for metric, avg in averages.items():
    print(f"{metric}: {avg:.4f}")
