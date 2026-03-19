import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def merge_missing_entries(json1_data, json2_data):
    existing_keys = {(entry["id"], entry["subid"]) for entry in json2_data}
    for entry in json1_data:
        key = (entry["id"], entry["subid"])
        if key not in existing_keys:
            json2_data.append(entry)
    json2_data.sort(key=lambda x: (int(x["id"]), int(x["subid"])))
    return json2_data

if __name__ == "__main__":
    json1_path = input("Enter path to source JSON file (full dataset): ").strip()
    json2_path = input("Enter path to target JSON file (partial dataset): ").strip()
    output_path = input("Enter output path for merged JSON file: ").strip()

    try:
        json1 = load_json(json1_path)
        json2 = load_json(json2_path)

        merged = merge_missing_entries(json1, json2)
        save_json(merged, output_path)

        print(f"✅ Merged JSON saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
