# Standard Imports
import logging
import time
import random

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


# Main Validation Function
def validate_inferred_example(example):
    """
    Validates a generated code example against the following validation classes:
    1. Strucutral Validation
    2. Compilation Success
    3. Functional Relevance
    4. Code Quality Check
    """

    inference_code = strip_c_comments(example["inference_code"])
    actual_code = strip_c_comments(example["output"])
    task = example["input"]
    filename = example["inference_file_name"]
    build_command = example["inference_build_command"]

    
    """
    1. Strucutral Validation
    This section evaluates the structure of the inferred code
    """

    # Main Function Presence Check
    if not has_main_function(inference_code):
        example["has_main_function"] = False
    else:
        example["has_main_function"] = True

    # Valid Include Directives Check
    if not has_valid_include(inference_code):
        example["has_include_directives"] = False
    else:
        example["has_include_directives"] = True

    # Must Have Libraries Check
    if not has_required_libraries(inference_code, C_RELEVANT_HEADERS):
        example["has_required_libraries"] = False
    else:
        example["has_required_libraries"] = True

    # CPP indicators Check
    valid, reasons = is_valid_c_code_with_no_cpp_indicator(inference_code)
    if valid:
        example["has_no_cpp_indicators"] = True
        example["cpp_indicators_details"] = None
    else:
        example["has_no_cpp_indicators"] = False
        example["cpp_indicators_details"] = reasons

    # Check for the presence of restricted headers and patterns
    violations = check_restricted_headers_and_patterns(inference_code)

    if violations:
        combined_lines = [f"{header} — {reason}" for header, reason in violations]
        full_message = (
            "Violations:\n" +
            "\n".join(f"  - {line}" for line in combined_lines)
        )
        example["has_no_restricted_headers_and_patterns"] = False
        example["restricted_headers_and_patterns_details"] = full_message
    else:
        example["has_no_restricted_headers_and_patterns"] = True
        example["restricted_headers_and_patterns_details"] = None

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
    # example["PercentageTaskRelevance_GEMINI"] = prepare_and_rate_sample_gemini(task, inference_code)
    example["PercentageTaskRelevance_GEMINI"] = 0
    # Wait before retrying
    #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

    # Check the code for relevancy against the already generated code - Gemini
    #example["PercentageCodeRelevanceToReference_GEMINI"] = compare_and_rate_inferred_code_gemini(task, inference_code, actual_code)
    example["PercentageCodeRelevanceToReference_GEMINI"] = 0
    #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

    ### GPT RATINGS ###
    # Check the code for relevancy against the task - GPT
    #example["PercentageTaskRelevance_GPT"] = prepare_and_rate_sample_gpt(task, inference_code)
    example["PercentageTaskRelevance_GPT"] = 0
    # Wait before retrying
    #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

    # Check the code for relevancy against the already generated code - GPT
    #example["PercentageCodeRelevanceToReference_GPT"] = compare_and_rate_inferred_code_gpt(task, inference_code, actual_code)
    example["PercentageCodeRelevanceToReference_GPT"] = 0

    # Wait before retrying
    #time.sleep(BASE_DELAY + random.uniform(0, JITTER))

    """
    2. Compilation Success and 4. Code Quality Check
    This section evaluates the structure of the inferred code
    """
    # Check syntax of the inferred code for the task
    example["inference_has_valid_syntax"], example["inference_syntax_check_message"], example["inference_warnings"] = validate_syntax(inference_code, filename)

    # Advanced level checks:
    # Check the build of the inferred code for the task
    example["inference_has_valid_build"], example["inference_build_message"] = validate_build(inference_code, filename, build_command)
    example["inference_static_code_quality_score"] = evaluate_code_quality_from_string(inference_code)

    return example


