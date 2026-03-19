import json
import re

def extract_gcc_command(code: str) -> str:
    """
    Extracts the first gcc compilation command found in the C code comments.
    Returns None if no such command is found.
    """
    gcc_match = re.search(r'gcc\s.*?(?=\n|\*/|$)', code, re.IGNORECASE)
    return gcc_match.group(0).strip() if gcc_match else None

def process_json_file(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        fallback = item.get("build-command", "")

        # Process finetuned_code
        finetuned_code = item.get("finetuned_code", "")
        ft_gcc = extract_gcc_command(finetuned_code)
        item["finetuned_build-command"] = ft_gcc if ft_gcc else fallback

        # Process base_code
        base_code = item.get("base_code", "")
        base_gcc = extract_gcc_command(base_code)
        item["base_build-command"] = base_gcc if base_gcc else fallback

    # Save updated data back
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    filename = input("Enter the path to your JSON file: ").strip()
    if filename:
        try:
            process_json_file(filename)
            print(f"Updated file: {filename}")
        except Exception as e:
            print(f"Error processing file: {e}")
    else:
        print("No filename provided. Exiting.")
