import json
import copy
from collections import OrderedDict

def insert_subid_after_id(obj, subid_value):
    """Insert 'subid' field right after 'id' field in a new OrderedDict."""
    new_obj = OrderedDict()
    for key, value in obj.items():
        new_obj[key] = value
        if key == "id":
            new_obj["subid"] = subid_value
    return new_obj

def main():
    input_filename = input("Enter the JSON file name to load (e.g., data.json): ")
    output_filename = input("Enter the output file name to save (e.g., expanded.json): ")

    try:
        with open(input_filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    if not isinstance(data, list):
        print("The JSON must contain a list of objects.")
        return

    expanded_data = []

    for item in data:
        # Original with subid = "0"
        original = insert_subid_after_id(item, "0")
        expanded_data.append(original)

        # First copy with subid = "1"
        copy1 = insert_subid_after_id(item, "1")
        expanded_data.append(copy1)

        # Second copy with subid = "2"
        copy2 = insert_subid_after_id(item, "2")
        expanded_data.append(copy2)

         # Second copy with subid = "3"
        copy3 = insert_subid_after_id(item, "3")
        expanded_data.append(copy3)

         # Second copy with subid = "4"
        copy4 = insert_subid_after_id(item, "4")
        expanded_data.append(copy4)

    try:
        with open(output_filename, 'w') as f:
            json.dump(expanded_data, f, indent=4)
        print(f"Expanded data written to {output_filename}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
