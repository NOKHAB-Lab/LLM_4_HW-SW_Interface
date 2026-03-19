# Standard Imports
import random
import logging
import time
import json
from datetime import datetime

# Configuration and function imports
from config.model import RPI_PICO, MAX_RETRIES, BASE_DELAY, JITTER, BUILD_AND_SYNTAX_VALIDATTION
from validation.correct_headers import replace_headers_in_output
from validation.validate import validate_code
from api.gemini_api import call_gemini_api  
from utils.formatting import extract_json_block_from_response, extract_c_code_from_output
from storage.example_saver import save_example
from validation.validate_build_command import build_command_looks_cpp
from validation.validate_build_and_compile import validate_build_and_compile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def repair_example(example):
    """
    Given an example with build and syntax errors, it repairs the examples
    """

    
    
    # Try multiple times in case of failure
    for attempt in range(MAX_RETRIES):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        example_id = example.get("id", "")
        
        fail_reason = ""  # initialized as empty string

        # Detailed Configuration Imports
        if RPI_PICO:
            repair_input = {
                "prompt": example.get("prompt", ""),
                "output": example.get("output", ""),
                "file_name": example.get("file-name", ""),
                "cmakelists": example.get("cmakelists", ""),
                "syntax_error": example.get("syntax_error", ""),
                "build_error": example.get("build_error", "")
            }
            
            generation_instruction_prompt = (
                "IMPORTANT FORMATTING REQUIREMENTS:"
                "Respond with a valid JSON object using the following structure: "
                "{"
                "\"output\": \"The complete fixed, valid, buildable C source code for Raspberry Pi Pico as a string\", "
                "\"explanation\": \"Brief explanation of how the code works (2 - 3 lines) \", "
                "\"file-name\": \"Suggested .c file name\", "
                "\"cmakelists\": \"The CMAKELISTS.txt program to compile the code using the CMAKE command\""
                "}. "
                "In the case of Raspberry Pi Pico, please generate the cmakelists.txt code only as we cannot run gcc for Raspberry Pi pico"
                "Avoid unnecessary formatting like markdown or triple backticks."
                "Please donot add anything with the output field of the response json i.e. the code, let it be purely C code. Dont add any Markdown formatting like (```c and ```)"
            )
        else:
            repair_input = {
                "prompt": example.get("prompt", ""),
                "output": example.get("output", ""),
                "file_name": example.get("file-name", ""),
                "build-command": example.get("build-command", ""),
                "syntax_error": example.get("syntax_error", ""),
                "build_error": example.get("build_error", "")
            }

            generation_instruction_prompt = (
                "IMPORTANT FORMATTING REQUIREMENTS:"
                "Respond with a valid JSON object using the following structure: "
                "{"
                "\"output\": \"The complete fixed, valid, buildable C source code for Raspberry Pi as a string\", "
                "\"explanation\": \"Brief explanation of how the code works (2 - 3 lines) \", "
                "\"file-name\": \"Suggested .c file name\", "
                "\"build-command\": \"Strictly only the gcc command to compile the code\""
                "}. "
                "Avoid unnecessary formatting like markdown or triple backticks."
                "Please donot add anything with the output field of the response json i.e. the code, let it be purely C code. Dont add any Markdown formatting like (```c and ```)"
            )
        repair_input_json = json.dumps(repair_input, indent=2)

        # Add extra instruction to ensure proper code format
        code_generation_prompt = f"""
            {repair_input_json}

        The above json shows the code in the "output" field generated against the "prompt" field. Analyze the errors in the fields "syntax_error" and "build_error" and correct the code in the output field.

        IMPORTANT Considerations while fixing the errors:
        1. Code should strictly be in C language and use libraries that support C programming.
        2. Donot use dummy libraries or non-standard libraries (such as sensor.h) etc.
        3. Donot refer to any C++ libraries in the code which cannot be used in a C program.
        4. Use modern and supported libraries like wiringPi, pigpio, bcm2835, or sysfs for accessing GPIO, I2C, SPI, and UART. Avoid old or deprecated libraries — they break on newer Raspberry Pi OS versions.
        5. Use only standard Raspberry Pi and Linux-compatible C libraries that can be installed via sudo apt-get or are commonly available on Raspberry Pi OS (Bookworm/Bullseye). Avoid proprietary or obscure libraries.
        6. Avoid deprecated libraries or functions. Ensure all APIs or commands used are compatible with modern Raspberry Pi OS (Bookworm/Bullseye).
        
        {generation_instruction_prompt}

        IMPORTANT Considerations
        Output must be a single raw JSON object without any commentary, explanation, or markdown syntax outside the JSON.

        IMPORTANT LAST INSTRUCTIONS:
        {fail_reason}
        """

        # Stage : Repairign the erraneous code based on the error and the instructions
        logger.info("Repairing code based on the shared error example")

        # Calling the API and validating generated content
        try:
            # Generate code with slightly higher temperature for creativity
            response_text = call_gemini_api(code_generation_prompt, temperature=0.75)

            if not response_text:
                logger.warning(f"Empty response from API, retrying ({attempt+1}/{MAX_RETRIES})")
                time.sleep(BASE_DELAY)
                continue
                
            # Extract and clean the response
            clean_json = extract_json_block_from_response(response_text)

            structured_data = json.loads(clean_json)  # Parse cleaned JSON
            # 🔥 FIX: Unwrap if it's a list
            if isinstance(structured_data, list):
                structured_data = structured_data[0]

            code = structured_data.get("output", "")
            
            # Filter unnecassary stuff from the code
            filtered_base_code = extract_c_code_from_output(code)
            
            # Update necassary headers
            filtered_code = replace_headers_in_output(filtered_base_code)

            # Update example object
            example["output"] = filtered_code
            example["explanation"] = structured_data.get("explanation", "")
            example["file-name"] = structured_data.get("file-name", "")
            example["timestamp"] = timestamp

            if not RPI_PICO:
                build_command = structured_data.get("build-command", "")
                example["build-command"] = structured_data.get("build-command", "")
            else:
                example["cmakelists"] = structured_data.get("cmakelists", "")

            # Validate code
            valid, fail_reason = validate_code(filtered_code, example, False)

            if not valid: 
                logger.warning(f"Repaired code failed validation, retrying ({attempt+1}/{MAX_RETRIES})")
                logger.info(f"Repaired code failed validation, reason: ({fail_reason})")
                continue

            # Validate build command
            if build_command_looks_cpp(build_command):
                logger.warning(f"Repaired code has incorrect build command, retrying ({attempt+1}/{MAX_RETRIES})")
                fail_reason = "Please generate a valid build command for the repaired C code on Raspberry Pi selected model. This command in the field above is invalid and has cpp fragments."
                logger.info("fail_reason: invalid build command (cpp type) for the repaired C code on Raspberry Pi selected model")
                continue
            else:
                return save_example(example, filtered_code)

            # # Validate syntax if requried
            # if BUILD_AND_SYNTAX_VALIDATTION:
            #     example, success, message = validate_build_and_compile(example)
            #     if not success:
            #         logger.info(f"Repaired code has failed syntax/build check ({attempt+1}/{MAX_RETRIES})")
            #         logger.warning(f"Failure reasons: {message}")
            #         fail_reason = message
            #         continue
            #     else:
            #         # Save the example with both the AI-generated prompt and the code, and other elements.
            #         return save_example(example, filtered_code)
                
        except Exception as e:
            logger.error(f"Error repairing example: {str(e)}")
        
        # Wait before retrying
        time.sleep(BASE_DELAY + random.uniform(0, JITTER))
    
    logger.error(f"Failed to repair example with id: {example_id} after {MAX_RETRIES} attempts")
    return False
