import json

# Ask user for filename
input_filename = input("Enter the name of the JSON file (e.g., data.json): ")

# Load JSON data
with open(input_filename, "r") as f:
    data = json.load(f)

# Extract first 20 entries with only selected fields and add 'source'
extracted = []
for item in data[:20]:
    extracted.append({
        "id": item.get("id"),
        "task": item.get("task"),
        "input": item.get("input"),
        "source": "validation_set"
    })

# Output result to new JSON file
output_filename = "validation_subset.json"
with open(output_filename, "w") as out:
    json.dump(extracted, out, indent=2)

print(f"Extracted 20 items and saved to {output_filename}")
