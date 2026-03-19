# Necassary imports
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration and function imports
from config.model import RPI_PICO, BASE_DIR

# Global list to collect all examples across sessions
all_examples = []
error_logs = [] # List to store erraneous parsed repsonse

# ----------------------------
# 🔹 Utility: Title Generator
# ----------------------------
def generate_task_title(category, subcategory, context):
    return f"Create a {subcategory.title()} {category.title()} Application for {context.title()}"

# ----------------------------
# 🔹 Utility: Tag Generator
# ----------------------------
def generate_tags(category, subcategory, context, pi_model, integration):
    tags = [category, subcategory]
    if context:
        tags.append(context.split()[-1])
    if pi_model:
        tags.append(pi_model.lower().replace(" ", "-"))
    if integration != "standalone":
        tags.append(integration.lower().replace(" ", "-"))
    return tags

# ----------------------------
# ✅ Save Individual Example
# ----------------------------
def save_example(structured_data, metadata, save_files = False):
    output_dir = BASE_DIR / "raspberry_pi_code_examples"
    try:
        # Generate a standard task title
        task_title = generate_task_title(metadata["category"], metadata["subcategory"], metadata["context"])
        generated_tags = generate_tags( # Generate standard task tags
            metadata["category"],
            metadata["subcategory"],
            metadata["context"],
            metadata["pi_model"],
            metadata["integration"]
        )

        # Generate timestamps and file information
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{metadata['category']}_{metadata['subcategory']}_{metadata['id']}_{timestamp}.c"
        filepath = os.path.join(output_dir, filename)

        try:
            # Fetch tags from the structured response (fallback to empty if not present)
            response_tags = structured_data.get("tags", "")
            filtered_code = structured_data.get("output", "")
            # Split response tags into a list if it's a string
            if isinstance(response_tags, str):
                response_tags = [tag.strip() for tag in response_tags.split(",") if tag.strip()]

            # Merge and deduplicate both lists
            combined_tags = list(sorted(set(generated_tags + response_tags)))
                
            if RPI_PICO:
                structured_response = {
                    "id": metadata["id"],
                    "task": task_title,
                    "category": structured_data.get("category", "ADC/DAC (Raspberry Pi, C Language)"),
                    "input": metadata["base_prompt"],
                    "prompt": metadata["generated_prompt"],
                    "output": filtered_code,
                    "explanation": structured_data.get("explanation", "Generated using Gemini API based on the given prompt."),
                    "complexity": metadata["complexity"],
                    "tags": ", ".join(combined_tags),
                    "file-name": structured_data.get("file-name", f"example_{metadata["id"]}.c"),
                    "cmakelists": structured_data.get("cmakelists", f"gcc example_{metadata["id"]}.c -o example_{metadata["id"]}"),
                    "timestamp": metadata["timestamp"]
                }
            else:
                 structured_response = {
                    "id": metadata["id"],
                    "task": task_title,
                    "category": structured_data.get("category", "ADC/DAC (Raspberry Pi, C Language)"),
                    "input": metadata["base_prompt"],
                    "prompt": metadata["generated_prompt"],
                    "output": filtered_code,
                    "explanation": structured_data.get("explanation", "Generated using Gemini API based on the given prompt."),
                    "complexity": metadata["complexity"],
                    "tags": ", ".join(combined_tags),
                    "file-name": structured_data.get("file-name", f"example_{metadata["id"]}.c"),
                    "build-command": structured_data.get("build-command", f"gcc example_{metadata["id"]}.c -o example_{metadata["id"]}"),
                    "timestamp": metadata["timestamp"]
                }
            all_examples.append(structured_response)
        except json.JSONDecodeError:
            print("⚠️ JSON Parsing Error: Storing raw response for debugging.")
            error_logs.append({"id": str(metadata["id"]), "raw_response": structured_data})
            

        if save_files: # if the parameter is true
            # Save code to .c file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"// Example-id: {metadata['id']}\n")
                f.write(f"// {task_title}\n")
                f.write(f"// Generated: {metadata['timestamp']}\n")
                f.write(f"// Complexity: {metadata['complexity']}, Style: {metadata['style']}\n")
                f.write(f"// Tags: {', '.join(combined_tags)}\n\n")
                if RPI_PICO:
                    f.write(f"// cmakelists: {structured_response["cmakelists"]}\n")
                else:
                    f.write(f"// Build-Command: {structured_response["build-command"]}\n")
                f.write(filtered_code)

        # Save data after each example generation
        with open(BASE_DIR / "pipeline_examples.json", "w", encoding="utf-8") as f:
            json.dump(all_examples, f, indent=4, ensure_ascii=False)

        # Save Error Logs Separately
        if error_logs:
            with open(BASE_DIR / "pipeline_errors.json", "w", encoding="utf-8") as f:
                json.dump(error_logs, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Saved example successfully: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save example: {e}")
        return False