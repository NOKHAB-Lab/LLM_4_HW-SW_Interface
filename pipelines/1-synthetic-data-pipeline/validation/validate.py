# Necassary imports
import re
import logging
from .validation_libraries import HEADER_CATEGORIES
from .validate_cpp_presence import is_valid_c_code_with_no_cpp_indicator
from .validate_illegal_libs import check_restricted_headers_and_patterns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Common required headers (used across Raspberry Pi C applications)
C_RELEVANT_HEADERS = [
    header
    for category in HEADER_CATEGORIES.values()
    for header in category
]

# ---------------------------
# 🔹 Submodule Functions
# ---------------------------

def strip_c_comments(code: str) -> str:
    """
    Remove both line (//...) and block (/*...*/) comments from C code.
    """
    # Remove block comments (/* ... */)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    # Remove line comments (//...)
    code = re.sub(r'//.*', '', code)

    return code

def has_main_function(code: str) -> bool:
    """Loosely check for presence of a main() function."""
    code_no_comments = strip_c_comments(code)

    # Match 'main' followed by optional whitespace/newlines and '('
    pattern = re.compile(r'\bmain\s*(\n|\s)*\(', re.IGNORECASE)

    if pattern.search(code_no_comments):
        return True

    logger.error("No `main()` function found.")
    return False

def has_valid_include(code: str) -> bool:
    """Check if #include directive is present outside of comments."""
    # Match lines that are not comments and contain #include
    include_pattern = re.compile(r'^\s*#include\s+[<"].+[>"]', re.MULTILINE)
    if include_pattern.search(code):
        return True
    logger.error("Missing valid `#include` directive.")
    return False

def has_required_libraries(code: str, required_headers: list) -> bool:
    """
    Checks for presence of any known C header/library from the provided list.
    Only considers actual #include lines to avoid false positives.
    """
    include_lines = re.findall(r'^\s*#include\s+[<"].+?[>"]', code, flags=re.MULTILINE)
    found_headers = [line for line in include_lines if any(header in line for header in required_headers)]

    if found_headers:
        return True
    logger.error("Required C libraries/headers not found in actual #include directives.")
    return False

def has_sufficient_comments(code: str, min_required=3) -> bool:
    """Ensure code includes a minimum number of useful comments (line-based)."""
    comment_lines = [
        line for line in code.splitlines()
        if line.strip().startswith("//") or "/*" in line or line.strip().startswith("*")
    ]
    count = len(comment_lines)

    if count >= min_required:
        return True

    logger.error(f"Too few comments found (found {count}, required {min_required}).")
    return False

def subcategory_match_fuzzy(code: str, subcategory: str) -> bool:
    """Loosely check if the subcategory or its components appear in the code or comments."""
    subcategory = subcategory.lower()
    code_lower = code.lower()

    # Direct match first
    if subcategory in code_lower:
        return True

    # Tokenize subcategory into keywords (skip generic ones)
    common_words_to_ignore = {"sensor", "value", "data", "input", "output", "control"}
    keywords = [word for word in re.findall(r'\w+', subcategory) if word not in common_words_to_ignore]

    # Extract comment lines
    comment_lines = [
        line.strip().lower()
        for line in code.splitlines()
        if "//" in line or "/*" in line
    ]

    # Check for any keyword match in comment lines
    for keyword in keywords:
        if any(re.search(rf"\b{keyword}\b", line) for line in comment_lines):
            return True

    return False

def has_error_handling(code: str) -> bool:
    if any(err in code for err in ["fprintf(stderr", "perror(", "return 1", "exit("]):
        return True
    logger.warning("Error handling/logging not detected.")
    return False

# ---------------------------
# ✅ Unified Validation Entry
# ---------------------------

def validate_code(code: str, subcategory: str) -> bool:
    """
    Validate the generated C code for Raspberry Pi programming.
    """
    with open('text_original.txt', 'w') as f:
        # Add header comment with metadata
        f.write(code)
    if not code or len(code) < 150:
        logger.error("Code too short.")
        return False, "Please make sure you generate a valid c code for Raspberry pi which is long enough to be functional."
    
    valid, reasons = is_valid_c_code_with_no_cpp_indicator(code)
    if not valid:
        logger.error("c++ elements found in code.")
        logger.error(reasons)
        return False, "Please make sure you generate a valid c code for Raspberry pi with no c++ elements. Avoid any c++ elements like: " + reasons

    if not has_main_function(code):
        logger.error("code has no main function.")
        return False, " Please make sure you generate a valid c code for Raspberry pi with a main function."

    if not has_valid_include(code):
        return False, "Please make sure you generate a valid c code for Raspberry pi with #include directives."

    if not has_required_libraries(code, C_RELEVANT_HEADERS):
        return False, "Please make sure you generate a valid c code for Raspberry pi with essential libraries."
    
    violations = check_restricted_headers_and_patterns(code)

    if violations:
        combined_lines = [f"{header} — {reason}" for header, reason in violations]
        full_message = (
            "Try to generate code without the following disallowed headers or libraries..\n"
            "Violations:\n" +
            "\n".join(f"  - {line}" for line in combined_lines)
        )
        return False, full_message

    # if not subcategory_match_fuzzy(code, subcategory):
    #     logger.error("Subcategory not detected in code or comments.")
    #     return False, "Please make sure you generate a valid c code for Raspberry pi mentioning the subcateogry: {subcategory}'s name in the comments."

    if not has_sufficient_comments(code):
        return False, "Please make sure you generate a valid c code for Raspberry pi with sufficient comments for the reader to understand"

    return True, ""
