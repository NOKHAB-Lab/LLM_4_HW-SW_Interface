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
def save_example(example, filtered_code, save_files = False):
    output_dir = BASE_DIR / "raspberry_pi_code_examples"
    try:
        # Generate timestamps and file information
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{example['category']}_{example['id']}_{timestamp}.c"
        filepath = os.path.join(output_dir, filename)

        all_examples.append(example)
            
        if save_files: # if the parameter is true
            # Save code to .c file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"// Example-id: {example['id']}\n")
                f.write(f"// {example['task']}\n")
                f.write(f"// Generated: {example['timestamp']}\n")
                f.write(f"// Complexity: {example['complexity']}\n")
                f.write(f"// Tags: {example['tags']}\n\n")
                if RPI_PICO:
                    f.write(f"// cmakelists: {example["cmakelists"]}\n")
                else:
                    f.write(f"// Build-Command: {example["build-command"]}\n")
                f.write(filtered_code)

        # Save data after each example generation
        with open(BASE_DIR / "repaired_examples.json", "w", encoding="utf-8") as f:
            json.dump(all_examples, f, indent=4, ensure_ascii=False)

        logger.info(f"Saved repaired example successfully: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save repaired example: {e}")
        return False