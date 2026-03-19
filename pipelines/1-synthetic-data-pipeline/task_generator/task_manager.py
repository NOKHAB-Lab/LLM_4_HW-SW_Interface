# Standard Imports
import random
import logging
import time
import json
from datetime import datetime

# Configuration and function imports
from config.model import RPI_PICO, MAX_RETRIES, BASE_DELAY, JITTER
from prompts.prompt_generator import generate_ai_prompt
from validation.validate import validate_code
from api.gemini_api import call_gemini_api  
from utils.formatting import extract_code, extract_json_block_from_response, extract_c_code_from_output
from storage.example_saver import save_example
from validation.validate_build_command import build_command_looks_cpp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Detailed Configuration Imports
if RPI_PICO:
    from config.constants_rpi_pico import (
        CODE_STYLES,
        COMPLEXITY_LEVELS,
        PI_MODELS,
        INTEGRATION_PATTERNS,
        USE_CONTEXTS,
        PROGRESSION_ORDER,
        CATEGORIES,
        PHASE_WEIGHTS
    )
else: 
    from config.constants_rpi_standard import (
        CODE_STYLES,
        COMPLEXITY_LEVELS,
        PI_MODELS,
        INTEGRATION_PATTERNS,
        USE_CONTEXTS,
        PROGRESSION_ORDER,
        CATEGORIES,
        PHASE_WEIGHTS
    )

def create_task_list(total_examples):
    """
    Generate a list of (category, subcategory, id) tuples to use for code generation.
    Ensures every subcategory is represented at least once, and adds more based on phase weights.
    """
    tasks = []
    example_id = 1

    # Include all defined subcategories (guaranteed coverage)
    for category in PROGRESSION_ORDER:
        for subcategory in CATEGORIES.get(category, []):
            tasks.append((category, subcategory, f"{example_id:04d}"))
            example_id += 1

    remaining = total_examples - len(tasks)

    # Generate remaining examples with weighted randomization from learning phases
    for _ in range(remaining):
        # Select phase (progressive category) based on weights
        phase = random.choices(
            list(PHASE_WEIGHTS.keys()), 
            weights=list(PHASE_WEIGHTS.values()), 
            k=1
        )[0]

        # Select random subcategory from that phase
        subcategory = random.choice(CATEGORIES[phase])
        
        tasks.append((phase, subcategory, f"{example_id:04d}"))
        example_id += 1

    # Shuffle tasks for better distribution during execution
    random.shuffle(tasks)
    return tasks


def generate_example(category, subcategory, example_id):
    """
    Given a category and subcategory, generate a full example.
    Includes prompt creation, Gemini API call, validation, and saving.
    """
    complexity = random.choice(COMPLEXITY_LEVELS)
    style = random.choice(CODE_STYLES)
    pi_model = random.choice(PI_MODELS)
    integration = random.choice(INTEGRATION_PATTERNS)
    context = random.choice(USE_CONTEXTS)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    fail_reason = ""  # initialized as empty string

    logger.info(f"🔧 Generating prompt for {category} → {subcategory}")
    base_prompt, ai_prompt = generate_ai_prompt(
        category, subcategory, complexity, style, pi_model, integration, context
    )

    metadata = {
        "id": example_id,
        "category": category,
        "subcategory": subcategory,
        "complexity": complexity,
        "style": style,
        "pi_model": pi_model,
        "integration": integration,
        "context": context,
        "timestamp": timestamp,
        "generated_prompt": ai_prompt,
        "base_prompt": base_prompt
    }

    # Detailed Configuration Imports
    if RPI_PICO:
        generation_instruction_prompt = (
            "IMPORTANT FORMATTING REQUIREMENTS:"
            "Respond with a valid JSON object using the following structure: "
            "{"
            "\"category\": \"Short description of the application\", "
            "\"input\": \"The original natural language prompt\", "
            "\"output\": \"The complete C source code as a string\", "
            "\"explanation\": \"Brief explanation of how the code works (2 - 3 lines) \", "
            "\"tags\": \"Comma-separated tags (e.g., Raspberry Pi, C, GPIO)\", "
            "\"file-name\": \"Suggested .c file name\", "
            "\"cmakelists\": \"The CMAKELISTS.txt program to compile the code using the CMAKE command\""
            "}. "
            "In the case of Raspberry Pi Pico, please generate the cmakelists.txt code only as we cannot run gcc for Raspberry Pi pico"
            "Avoid unnecessary formatting like markdown or triple backticks."
            "Please donot add anything with the output field of the response json i.e. the code, let it be purely C code. Dont add any Markdown formatting like (```c and ```)"
        )
    else:
        generation_instruction_prompt = (
            "IMPORTANT FORMATTING REQUIREMENTS:"
            "Respond with a valid JSON object using the following structure: "
            "{"
            "\"category\": \"Short description of the application\", "
            "\"input\": \"The original natural language prompt\", "
            "\"output\": \"The complete C source code as a string\", "
            "\"explanation\": \"Brief explanation of how the code works (2 - 3 lines) \", "
            "\"tags\": \"Comma-separated tags (e.g., Raspberry Pi, C, GPIO)\", "
            "\"file-name\": \"Suggested .c file name\", "
            "\"build-command\": \"The gcc or make command to compile the code\""
            "}. "
            "Avoid unnecessary formatting like markdown or triple backticks."
            "Please donot add anything with the output field of the response json i.e. the code, let it be purely C code. Dont add any Markdown formatting like (```c and ```)"
        )

    # Add extra instruction to ensure proper code format
    code_generation_prompt = f"""
        {ai_prompt}

    IMPORTANT GENERATION INSTRUCTIONS:
    {generation_instruction_prompt}

    IMPORTANT Considerations
    1. Ensure the C code: uses proper headers, includes error checking, is realistic for embedded applications, and is written clearly with helpful comments.
    2. For logging, use either file-based (`fopen`, `fprintf`) or terminal (`printf`) output.
    3. Code must compile independently, no placeholders or pseudocode.
    4. Randomize the formatting of comments — use inline, block-style, or no comments at all.
    5. Use different flow structures: `while`, `for`, `do-while`, or `if` + `sleep()` instead of polling.
    6. Sometimes use signal handling (`signal(SIGINT, ...)`) for graceful shutdown.
    🔥 Bonus Variations (Occasionally Introduce):
    - Use `struct` for grouping configuration or runtime state.
    - Create helper functions to modularize logic (setup(), read_sensor(), log_data(), etc.).
    - Implement basic retry logic if sensor read fails.
    - Use `gettimeofday()` or `time()` for timestamping if logging.
    
    Output must be a single raw JSON object without any commentary, explanation, or markdown syntax outside the JSON.
    Ensure GPIO, sensor, or communication logic is realistic and platform-specific

    IMPORTANT LAST INSTRUCTIONS:
    {fail_reason}
    """


    # Stage 2: Generate the actual code using the AI-created prompt
    logger.info("Generating code based on AI prompt")
    
    # Try multiple times in case of failure
    for attempt in range(MAX_RETRIES):
        try:
            # Generate code with slightly higher temperature for creativity
            response_text = call_gemini_api(code_generation_prompt, temperature=0.75)
            with open('text_original.txt', 'w') as f:
                # Add header comment with metadata
                f.write(response_text)
            if not response_text:
                logger.warning(f"Empty response from API, retrying ({attempt+1}/{MAX_RETRIES})")
                time.sleep(BASE_DELAY)
                continue
                
            # Extract and clean the response
            clean_json = extract_json_block_from_response(response_text)
            with open('clean_json.txt', 'w') as f:
                # Add header comment with metadata
                f.write(clean_json)

            structured_data = json.loads(clean_json)  # Parse cleaned JSON
            # 🔥 FIX: Unwrap if it's a list
            if isinstance(structured_data, list):
                structured_data = structured_data[0]
            
            with open('structured_data.txt', 'w') as f:
                # Add header comment with metadata
                f.write(clean_json)
            
            code = structured_data.get("output", "")
            filtered_code = extract_c_code_from_output(code)
            build_command = structured_data.get("build-command", "")

            valid, fail_reason = validate_code(filtered_code, subcategory)

            # Validate the code
            if valid:
                if not build_command_looks_cpp(build_command):
                    # Save the example with both the AI-generated prompt and the code, and other elements.
                    return save_example(structured_data, metadata)
                else:
                    logger.warning(f"Generated code has incorrect build command, retrying ({attempt+1}/{MAX_RETRIES})")
                    fail_reason = "Please generated a valid build command for the generated C code on {pi_model}"
            else:
                logger.warning(f"Generated code failed validation, retrying ({attempt+1}/{MAX_RETRIES})")
        except Exception as e:
            logger.error(f"Error generating example: {str(e)}")
        
        # Wait before retrying
        time.sleep(BASE_DELAY + random.uniform(0, JITTER))
    
    logger.error(f"Failed to generate valid example for {category}/{subcategory} after {MAX_RETRIES} attempts")
    return False
