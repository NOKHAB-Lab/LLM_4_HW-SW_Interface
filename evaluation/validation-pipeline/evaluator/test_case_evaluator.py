import logging

logger = logging.getLogger(__name__)

def evaluate_test_cases(validation_metrics: dict) -> dict:
    """
    Evaluate individual test cases and return test case results.
    
    Returns:
        dict with two keys:
        - 'test_case_validation': dict of 5 test case statuses
        - 'all_test_cases_passed': bool
    """
    logger.info(f"Starting test case validation for base code..........")
    # Extract booleans and int safely
    has_main = bool(validation_metrics.get("has_main_function", 0))
    no_restricted_headers = bool(validation_metrics.get("has_no_restricted_headers_and_patterns", 0))
    no_cpp_elements = bool(validation_metrics.get("has_no_cpp_indicators", 0))
    valid_syntax = bool(validation_metrics.get("inference_has_valid_syntax", 0))
    successful_build = bool(validation_metrics.get("inference_has_valid_build", 0))
    quality_rating = validation_metrics.get("inference_static_code_quality_score", 1)

    if not (1 <= quality_rating <= 5):
        logger.warning(f"Quality_rating '{quality_rating}' out of range [1–5], defaulting to 1")
        quality_rating = 1

    # Individual test case checks
    test_case_1 = has_main
    test_case_2 = no_restricted_headers and no_cpp_elements
    test_case_3 = valid_syntax
    test_case_4 = successful_build
    test_case_5 = quality_rating >= 4

    all_test_cases_passed = all([test_case_1, test_case_2, test_case_3, test_case_4, test_case_5])
    logger.info(f"Ending test case validation for base code..........")
    test_cases_object = {
            "test_case_1_mainFunction_status": test_case_1,
            "test_case_2_restrictedElements_status": test_case_2,
            "test_case_3_syntax_status": test_case_3,
            "test_case_4_compile_status": test_case_4,
            "test_case_5_qualityCritiera_status": test_case_5
        }
    return test_cases_object, all_test_cases_passed