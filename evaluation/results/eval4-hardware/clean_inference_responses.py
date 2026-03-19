import json
import re
from pathlib import Path

import re

def clean_mistral_c_output(full_text: str) -> str:
    """
    Cleans Mistral-generated output by:
    - Removing <s><s>[INST] ... [/INST] parts
    - Removing markdown artifacts like ```
    - Removing trailing build/meta sections
    - Removing unclosed trailing comment tokens (/* or //)
    """
    # Step 1: Remove <s><s>[INST] ... [/INST] wrapper
    full_text = re.sub(r"<s><s>\[INST\].*?\[/INST\]", "", full_text, flags=re.DOTALL).strip()

    # Step 2: Remove markdown triple backticks
    full_text = re.sub(r"```[cC]*", "", full_text).strip()

    # Step 3: Cut off known trailing meta/documentation sections
    stop_markers = [
        r"^\s*To compile:", r"^\s*To run:", r"^\s*Compilation instructions:",
        r"^\s*Execution instructions:", r"^\s*Assumptions:", r"^\s*Limitations:",
        r"^\s*Potential Improvements:", r"^\s*Security Considerations:",
        r"^\s*Environmental Considerations:", r"^\s*Disclaimer:", r"^\s*License:",
        r"^\s*Testing:", r"^\s*Future Improvements:", r"^\s*Troubleshooting:",
        r"^\s*Development Environment:", r"^\s*Version Control:", r"^\s*Code Review:",
        r"^\s*Revision History:", r"^\s*Appendices:", r"^\s*References:", r"^\s*Copyright:"
    ]
    stop_pattern = re.compile("|".join(stop_markers), re.IGNORECASE | re.MULTILINE)
    match = stop_pattern.search(full_text)
    if match:
        full_text = full_text[:match.start()].strip()

    # Step 4: Remove any incomplete trailing comment block
    full_text = re.sub(r"/\*\s*$", "", full_text)
    full_text = re.sub(r"//\s*$", "", full_text)

    # Step 5: Remove anything after `return 0; }` if followed by dangling `/*`
    full_text = re.sub(r"(return\s+0;\s*\}\s*)/\*.*", r"\1", full_text, flags=re.DOTALL)

    return full_text.strip()

def process_json_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read JSON: {e}")
        return

    if not isinstance(data, list):
        print("❌ Error: JSON root is not a list of objects.")
        return

    updated = 0
    for obj in data:
        if "inference_response" in obj:
            raw = obj["inference_response"]
            obj["inference_code"] = clean_mistral_c_output(raw)
            updated += 1

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Processed {updated} entries in: {file_path}")
    except Exception as e:
        print(f"❌ Failed to write JSON: {e}")


if __name__ == "__main__":
    user_input = input("Enter path to JSON file: ").strip()
    file_path = Path(user_input)

    if not file_path.is_file():
        print(f"❌ File not found: {file_path}")
    else:
        process_json_file(str(file_path))
