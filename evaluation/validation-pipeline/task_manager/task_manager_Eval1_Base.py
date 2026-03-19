# Standard Imports
import logging
import time
import random
import re

# Configuration and function imports
# Structural Validations
from validation.validate import has_main_function, has_valid_include, strip_c_comments, has_required_libraries, has_error_handling, C_RELEVANT_HEADERS 
from validation.validate_cpp_presence import is_valid_c_code_with_no_cpp_indicator
from validation.validate_illegal_libs import check_restricted_headers_and_patterns

# Functional Relevancy Validations
from validation.validation_task_accuracy_gemini import prepare_and_rate_sample_gemini, compare_and_rate_inferred_code_gemini
from validation.validation_task_accuracy_gpt import prepare_and_rate_sample_gpt, compare_and_rate_inferred_code_gpt

# Compilation Success
from validation.validate_build_and_compile import validate_syntax, validate_build

# Code Quality Check
from validation.validate_static_code_quality import evaluate_code_quality_from_string

# Necassary parameters
from config.model import BASE_DELAY, JITTER

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_build_command(base_build_command):
    commands = base_build_command.split('\n')
    build_cmd = None
    for cmd in commands:
        if cmd.strip().startswith('gcc'):
            build_cmd = cmd.strip()
            break
    if not build_cmd:
        return None, None
    tokens = build_cmd.split()
    c_filename = None
    for token in tokens:
        if token.endswith('.c'):
            c_filename = token
            break
    return build_cmd, c_filename

def select_build_command(base_build_command, file_name, build_command):
    """
    Selects the build command and .c filename, using base_build_command if it contains gcc,
    otherwise falling back to the provided build_command and file_name.
    
    Args:
        base_build_command (str): The base build command string from the JSON.
        file_name (str): The filename field (e.g., "sht31_monitor.c").
        build_command (str): The fallback build command (e.g., "gcc -O3 sht31_monitor.c -o sht31_monitor -lpigpio -lrt").
    
    Returns:
        tuple: (build_cmd, c_filename) where build_cmd is the selected build command,
               and c_filename is the extracted .c filename.
    """
    # Try to parse the base_build_command
    build_cmd, c_filename = parse_build_command(base_build_command)
    
    # If no gcc command found in base_build_command, use the provided build_command and file_name
    if not build_cmd:
        build_cmd = build_command.strip()
        # Extract .c filename from file_name if provided, otherwise from build_command
        if file_name and file_name.endswith('.c'):
            c_filename = file_name
        else:
            tokens = build_cmd.split()
            c_filename = next((token for token in tokens if token.endswith('.c')), None)
    
    return build_cmd, c_filename

# Main Validation Function
def validate_inferred_example_base(example, only_compiler_validation: bool = False):
    """
    Validates the base code against the following validation classes:
    1. Strucutral Validation
    2. Compilation Success
    3. Functional Relevance
    4. Code Quality Check
    """

    inference_code = strip_c_comments(example.get("base_code", ""))
    actual_code = strip_c_comments(example.get("output", ""))
    task = example.get("input", "")

    base_build_command = example.get("base_build-command", "")
    #logger.error(f"base build_command initial: {base_build_command}")
    source_file_name = example.get("file-name", "")
    source_build_command = example.get("build-command", "")
    build_command, filename = select_build_command(base_build_command, source_file_name, source_build_command)
    #logger.error(f"base filename: {filename}")
    #logger.error(f"base build_command: {build_command}")   
    # Main Function Presence Check

    if not only_compiler_validation:
        if not has_main_function(inference_code):
            example["base_has_main_function"] = False
        else:
            example["base_has_main_function"] = True

        # Valid Include Directives Check
        if not has_valid_include(inference_code):
            example["base_has_include_directives"] = False
        else:
            example["base_has_include_directives"] = True

        # Must Have Libraries Check
        if not has_required_libraries(inference_code, C_RELEVANT_HEADERS):
            example["base_has_required_libraries"] = False
        else:
            example["base_has_required_libraries"] = True

        # CPP indicators Check
        valid, reasons = is_valid_c_code_with_no_cpp_indicator(inference_code)
        if valid:
            example["base_has_no_cpp_indicators"] = True
            example["base_cpp_indicators_details"] = None
        else:
            example["base_has_no_cpp_indicators"] = False
            example["base_cpp_indicators_details"] = reasons

        # Check for the presence of restricted headers and patterns
        violations = check_restricted_headers_and_patterns(inference_code)

        if violations:
            combined_lines = [f"{header} — {reason}" for header, reason in violations]
            full_message = (
                "Violations:\n" +
                "\n".join(f"  - {line}" for line in combined_lines)
            )
            example["base_has_no_restricted_headers_and_patterns"] = False
            example["base_restricted_headers_and_patterns_details"] = full_message
        else:
            example["base_has_no_restricted_headers_and_patterns"] = True
            example["base_restricted_headers_and_patterns_details"] = None

        # Intermediate level checks:

        # Check the code for error handling    
        #if has_error_handling:
        #    example["has_error_handling"] = False
        #else:
        #    example["has_error_handling"] = True

        """
        3. Functional Relevance Check
        This section evaluates the functional relevance between the task, inferred code and the sample code as well
        """

        ### GEMINI RATINGS ###
        # Check the code for relevancy against the task - Gemini
        #example["base_PercentageTaskRelevance_GEMINI"] = prepare_and_rate_sample_gemini(task, inference_code)
        example["base_PercentageTaskRelevance_GEMINI"] = 0
        # Wait before retrying
        #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

        # Check the code for relevancy against the already generated code - Gemini
        #example["base_PercentageCodeRelevanceToReference_GEMINI"] = compare_and_rate_inferred_code_gemini(task, inference_code, actual_code)
        example["base_PercentageCodeRelevanceToReference_GEMINI"] = 0
        # Wait before retrying
        #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

        ### GPT RATINGS ###
        # Check the code for relevancy against the task - GPT
        #example["base_PercentageTaskRelevance_GPT"] = prepare_and_rate_sample_gpt(task, inference_code)
        example["base_PercentageTaskRelevance_GPT"] = 0
        # Wait before retrying
        #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

        # Check the code for relevancy against the already generated code - GPT
        #example["base_PercentageCodeRelevanceToReference_GPT"] = compare_and_rate_inferred_code_gpt(task, inference_code, actual_code)
        example["base_PercentageCodeRelevanceToReference_GPT"] = 0
        # Wait before retrying
        #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

    """
    2. Compilation Success and 4. Code Quality Check
    This section evaluates the structure of the inferred code
    """
    # Check syntax of the inferred code for the task
    example["base_inference_has_valid_syntax"], example["base_inference_syntax_check_message"], example["base_inference_warnings"] = validate_syntax(inference_code, filename)

    # Advanced level checks:
    # Check the build of the inferred code for the task
    example["base_inference_has_valid_build"], example["base_inference_build_message"] = validate_build(inference_code, filename, build_command)
    example["base_inference_static_code_quality_score"] = evaluate_code_quality_from_string(inference_code)

    return example


