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
    "statuses": {}
})

# Populate the grouped dictionary
for item in data:
    example_id = item["id"]
    sub_id = int(item["subid"])

    grouped[example_id]["category"] = item["category"]
    grouped[example_id]["statuses"][sub_id] = item.get("all_test_cases_execution_status", False)

# Generate the output rows
rows = []
for example_id, info in grouped.items():
    statuses = info["statuses"]

    row = {
        "category": info["category"],
        "pass@1": int(statuses.get(0, False)),
        "pass@3": int(any(statuses.get(i, False) for i in range(3))),
        "pass@5": int(any(statuses.get(i, False) for i in range(5))),
    }
    rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv("evaluation_pass_summary.csv", index=False)
print("Saved to evaluation_pass_summary.csv")

# Compute overall averages
metrics = ["pass@1", "pass@3", "pass@5"]
averages = {metric: df[metric].mean() for metric in metrics}

print("\nOverall Averages:")
for metric, avg in averages.items():
    print(f"{metric}: {avg:.4f}")
