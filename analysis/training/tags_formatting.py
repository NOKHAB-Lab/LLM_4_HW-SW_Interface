import json
import os

def process_json_tags(filepath):
    """
    Processes a JSON file to ensure 'tags' are lists of strings.
    Converts comma-separated tag strings to lists and counts updated objects.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        int: The number of objects whose tags were updated.
    """
    updated_object_count = 0

    # Check if the file exists
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        return 0
    
    # Check if the file is empty
    if os.stat(filepath).st_size == 0:
        print(f"Error: The file '{filepath}' is empty.")
        return 0

    try:
        with open(filepath, 'r+') as f:
            data = json.load(f)

            # Ensure data is a list, if not, wrap it in a list
            if not isinstance(data, list):
                data = [data]
                
            for obj in data:
                if 'tags' in obj:
                    current_tags = obj['tags']

                    # Check if tags are a comma-separated string
                    if isinstance(current_tags, str):
                        obj['tags'] = [tag.strip() for tag in current_tags.split(',')]
                        updated_object_count += 1
                    # Check if tags are a list, but contain non-string elements
                    elif isinstance(current_tags, list):
                        needs_update = False
                        for i, tag in enumerate(current_tags):
                            if not isinstance(tag, str):
                                current_tags[i] = str(tag).strip()
                                needs_update = True
                        if needs_update:
                            updated_object_count += 1
                    # If tags are neither a string nor a list, convert to an empty list
                    else:
                        obj['tags'] = []
                        updated_object_count += 1

            f.seek(0)  # Rewind to the beginning of the file
            json.dump(data, f, indent=2)
            f.truncate() # Remove remaining part if new data is shorter

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'. Please ensure it's a valid JSON file.")
        return 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 0

    return updated_object_count

# --- Main execution ---
if __name__ == "__main__":
    file_path = input("Please enter the name of your JSON file (e.g., data.json or /path/to/data.json): ")
    num_updated = process_json_tags(file_path)

    if num_updated > 0:
        print(f"\nSuccessfully processed '{file_path}'.")
        print(f"Number of objects with updated tags: {num_updated}")
    elif num_updated == 0 and os.path.exists(file_path) and os.stat(file_path).st_size > 0:
        print(f"\nNo tags needed updating in '{file_path}'. All tags were already in the correct format.")
    # Error messages are printed directly from the function