import json
import os

# Prompt the user for the JSON file name
json_filename = input("Enter the name of the JSON file (e.g., sensor_examples.json): ").strip()

# Check if file exists
if not os.path.exists(json_filename):
    print(f"Error: File '{json_filename}' not found.")
    exit(1)

# Load the JSON data
with open(json_filename, "r") as f:
    data = json.load(f)

# Output files
finetuned_output = "finetuned_failures.txt"
base_output = "base_failures.txt"

with open(finetuned_output, "w") as fout_fine, open(base_output, "w") as fout_base:
    for example in data:
        example_id = example.get("id", "N/A")
        task = example.get("task", "No task provided.")

        # Process fine-tuned model validation
        ft_has_syntax = example.get("finetuned_inference_has_valid_syntax", True)
        ft_has_build = example.get("finetuned_inference_has_valid_build", True)

        if not ft_has_syntax or not ft_has_build:
            fout_fine.write(f"ID: {example_id}\n")
            fout_fine.write(f"Task: {task}\n")
            if not ft_has_syntax:
                fout_fine.write(f"{example.get('finetuned_inference_syntax_check_message', 'No syntax message')}\n")
            if not ft_has_build:
                fout_fine.write(f"{example.get('finetuned_inference_build_message', 'No build message')}\n")
            fout_fine.write("\n")

        # Process base model validation
        base_has_syntax = example.get("base_inference_has_valid_syntax", True)
        base_has_build = example.get("base_inference_has_valid_build", True)

        if not base_has_syntax or not base_has_build:
            fout_base.write(f"ID: {example_id}\n")
            fout_base.write(f"Task: {task}\n")
            if not base_has_syntax:
                fout_base.write(f"{example.get('base_inference_syntax_check_message', 'No syntax message')}\n")
            if not base_has_build:
                fout_base.write(f"{example.get('base_inference_build_message', 'No build message')}\n")
            fout_base.write("\n")

print(f"Done. Failures written to '{finetuned_output}' and '{base_output}'.")
