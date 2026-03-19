import logging

logger = logging.getLogger(__name__)

def safe_clamp_int(value, label):
    if not isinstance(value, int):
        logger.warning(f"{label} is not an integer: '{value}', setting to 0")
        return 0
    if not (0 <= value <= 100):
        logger.warning(f"{label} '{value}' out of range [0-100], clamped to 0-100")
    return max(0, min(100, value))


def calculate_code_accuracy_base(validation_metrics: dict) -> tuple[float, dict]:
    """
    Calculate the overall accuracy of a code sample based on validation metrics provided in a dictionary.
    
    Args:
        validation_metrics (dict): Dictionary containing the following fields:
            - has_main_function (bool): Code includes main() function.
            - has_required_libraries (bool): Code uses required libraries.
            - has_no_restricted_headers_and_patterns (bool): Code has no restricted/custom headers.
            - has_no_cpp_indicators (bool): Code has no C++ elements.
            - has_include_directives (bool): Code has include directives.
            - inference_has_valid_syntax (bool): Code has valid syntax.
            - inference_has_valid_build (bool): Code builds successfully.
            - PercentageTaskRelevance_GEMINI (int): % relevancy to task (Gemini, 0-100).
            - PercentageTaskRelevance_GPT (int): % relevancy to task (GPT, 0-100).
            - PercentageCodeRelevanceToReference_GEMINI (int): % relevancy to reference (Gemini, 0-100).
            - PercentageCodeRelevanceToReference_GPT (int): % relevancy to reference (GPT, 0-100).
            - inference_static_code_quality_score (int): Static code quality rating (1-5).
            - inference_warnings (int): Number of compiler warnings.
    
    Returns:
        tuple[float, dict]: (overall_accuracy, breakdown)
            - overall_accuracy: Total accuracy percentage (0-100).
            - breakdown: Dict with scores per validation class.
    """
    
    # Extract fields with defaults to handle missing keys
    has_main = validation_metrics.get("base_has_main_function", 0)
    uses_required_libraries = validation_metrics.get("base_has_required_libraries", 0)
    no_restricted_headers = validation_metrics.get("base_has_no_restricted_headers_and_patterns", 0)
    no_cpp_elements = validation_metrics.get("base_has_no_cpp_indicators", 0)
    has_include_directives = validation_metrics.get("base_has_include_directives", 0)
    valid_syntax = validation_metrics.get("base_inference_has_valid_syntax", 0)
    successful_build = validation_metrics.get("base_inference_has_valid_build", 0)
    relevancy_task_gemini = validation_metrics.get("base_PercentageTaskRelevance_GEMINI", 0)
    relevancy_task_gpt = validation_metrics.get("base_PercentageTaskRelevance_GPT", 0)
    relevancy_reference_gemini = validation_metrics.get("base_PercentageCodeRelevanceToReference_GEMINI", 0)
    relevancy_reference_gpt = validation_metrics.get("base_PercentageCodeRelevanceToReference_GPT", 0)
    quality_rating = validation_metrics.get("base_inference_static_code_quality_score", 1)  # Default to lowest rating
    compiler_warnings = validation_metrics.get("base_inference_warnings", 0)

    # Validate and convert boolean-like integers (1 = True, 0 = False)
    has_main = bool(has_main) if has_main in (0, 1) else (logger.warning(f"Invalid has_main value '{has_main}', defaulting to False"), False)
    uses_required_libraries = bool(uses_required_libraries) if uses_required_libraries in (0, 1) else (logger.warning(f"Invalid uses_required_libraries value '{uses_required_libraries}', defaulting to False"), False)
    no_restricted_headers = bool(no_restricted_headers) if no_restricted_headers in (0, 1) else (logger.warning(f"Invalid no_restricted_headers value '{no_restricted_headers}', defaulting to False"), False)
    no_cpp_elements = bool(no_cpp_elements) if no_cpp_elements in (0, 1) else (logger.warning(f"Invalid no_cpp_elements value '{no_cpp_elements}', defaulting to False"), False)
    has_include_directives = bool(has_include_directives) if has_include_directives in (0, 1) else (logger.warning(f"Invalid has_include_directives value '{has_include_directives}', defaulting to False"), False)
    valid_syntax = bool(valid_syntax) if valid_syntax in (0, 1) else (logger.warning(f"Invalid valid_syntax value '{valid_syntax}', defaulting to False"), False)
    successful_build = bool(successful_build) if successful_build in (0, 1) else (logger.warning(f"Invalid successful_build value '{successful_build}', defaulting to False"), False)

    # Validate relevancy percentages (0-100)
    relevancy_task_gemini       = safe_clamp_int(relevancy_task_gemini, "relevancy_task_gemini")
    relevancy_task_gpt          = safe_clamp_int(relevancy_task_gpt, "relevancy_task_gpt")
    relevancy_reference_gemini  = safe_clamp_int(relevancy_reference_gemini, "relevancy_reference_gemini")
    relevancy_reference_gpt     = safe_clamp_int(relevancy_reference_gpt, "relevancy_reference_gpt")


    # Validate quality rating (1-5)
    if not (1 <= quality_rating <= 5):
        logger.warning(f"Quality_rating '{quality_rating}' out of range [1-5], defaulting to 1")
        quality_rating = 1

    # Initialize breakdown dictionary for each validation class
    breakdown = {
        "Structural_Validation": 0.0,
        "Compilation_Success": 0.0,
        "Functional_Relevance": 0.0,
        "Code_Quality_Check": 0.0
    }

    # Structural Validation (40% total)
    structural_score = 0.0
    if has_main:
        structural_score += 10.0  # Code includes main()
    if uses_required_libraries:
        structural_score += 10.0  # Uses required libraries
    if no_restricted_headers:
        structural_score += 10.0  # No restricted/custom headers
    if no_cpp_elements:
        structural_score += 5.0   # No C++ elements
    if has_include_directives:
        structural_score += 5.0   # Has include directives
    breakdown["Structural_Validation"] = structural_score

    # Compilation Success (25% total)
    compilation_score = 0.0
    if valid_syntax:
        compilation_score += 10.0  # Valid syntax
    if successful_build:
        compilation_score += 15.0  # Successful build
    breakdown["Compilation_Success"] = compilation_score

    # Functional Relevance (25% total)
    # Scale relevancy integers by their weights
    functional_score = 0.0
    functional_score += (relevancy_task_gemini / 100.0) * 10.0  # % relevancy to task - Gemini
    functional_score += (relevancy_task_gpt / 100.0) * 10.0    # % relevancy to task - GPT
    functional_score += (relevancy_reference_gemini / 100.0) * 2.5  # % relevancy to reference - Gemini
    functional_score += (relevancy_reference_gpt / 100.0) * 2.5     # % relevancy to reference - GPT
    breakdown["Functional_Relevance"] = functional_score

    # Code Quality Check (15% total)
    quality_score = 0.0
    # Scale quality rating (1-5) to a percentage, then apply its 5% weight
    quality_percentage = (quality_rating / 5.0) * 100.0
    quality_score += (quality_percentage / 100.0) * 5.0  # Static code quality rating
    # Compiler warnings: 5% for 0 warnings, 0% for 5+ warnings, linear decrease
    warnings_score = max(0, 5 - compiler_warnings)  # 5 warnings or more = 0%
    quality_score += (warnings_score / 5.0) * 5.0   # Apply 5% weight
    breakdown["Code_Quality_Check"] = quality_score

    # Overall accuracy
    overall_accuracy = (
        structural_score +
        compilation_score +
        functional_score +
        quality_score
    )

    return overall_accuracy, breakdown
