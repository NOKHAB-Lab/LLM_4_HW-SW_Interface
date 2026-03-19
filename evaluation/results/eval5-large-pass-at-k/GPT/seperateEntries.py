import json

# Load both JSON files
input_file1 = input("Enter the source JSON filename (entries to check): ").strip()
input_file2 = input("Enter the reference JSON filename (entries to compare against): ").strip()

with open(input_file1, "r") as f1:
    data1 = json.load(f1)

with open(input_file2, "r") as f2:
    data2 = json.load(f2)

# Build a set of (id, subid) pairs from JSON 2
existing_keys = set((item["id"], item["subid"]) for item in data2)

# Find missing entries from JSON 1
missing_entries = [item for item in data1 if (item["id"], item["subid"]) not in existing_keys]

# Write the missing entries to a new file
with open("missing_entries.json", "w") as f_out:
    json.dump(missing_entries, f_out, indent=2)

print(f"{len(missing_entries)} entries written to missing_entries.json")
