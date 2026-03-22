import json
from collections import defaultdict

# List of input JSON files
input_files = ["GPT_Missing_Output_Responses.json", "gpt_responses_70by5_large.json", "missing_entries1.json"]

# Load and combine all data
combined_data = []
for file in input_files:
    with open(file, "r") as f:
        combined_data.extend(json.load(f))

# Group by ID and collect subid-sorted entries
grouped = defaultdict(list)
for entry in combined_data:
    grouped[entry["id"]].append(entry)

# Sort by id (as int) and subid (as int)
sorted_result = []
for id_key in sorted(grouped.keys(), key=lambda x: int(x)):
    entries = grouped[id_key]
    sorted_entries = sorted(entries, key=lambda x: int(x["subid"]))
    sorted_result.extend(sorted_entries)

# Save the final merged and sorted JSON
with open("merged_sorted.json", "w") as out_file:
    json.dump(sorted_result, out_file, indent=2)

print(f"Merged and sorted JSON written to merged_sorted.json with {len(sorted_result)} entries.")
