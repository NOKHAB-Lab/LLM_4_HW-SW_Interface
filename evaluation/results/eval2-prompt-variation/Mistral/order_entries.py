import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def reorder_json_by_reference(reference_data, target_data):
    # Build a lookup for target entries
    target_lookup = {(item['id'], item['subid']): item for item in target_data}

    # Reorder target to match the order in reference
    ordered = [
        target_lookup[(item['id'], item['subid'])]
        for item in reference_data
        if (item['id'], item['subid']) in target_lookup
    ]

    return ordered

if __name__ == "__main__":
    reference_path = input("Enter path to reference JSON (json1): ").strip()
    target_path = input("Enter path to target JSON to reorder (json2): ").strip()
    output_path = input("Enter path to save reordered JSON: ").strip()

    try:
        reference_data = load_json(reference_path)
        target_data = load_json(target_path)

        reordered = reorder_json_by_reference(reference_data, target_data)
        save_json(reordered, output_path)

        print(f"✅ Reordered JSON saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
