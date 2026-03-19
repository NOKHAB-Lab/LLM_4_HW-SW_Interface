import logging

logger = logging.getLogger(__name__)

# Map of deprecated or incorrect headers to their correct replacements.
# Extend this dict as needed for your embedded C environment.
HEADER_REPLACEMENTS = {
    # Example: "#include <wiringPiI2C.h>" is correct — no replacements defined by default.
}

def replace_headers_in_output(code: str) -> str:
    """
    Scans the generated C code for known deprecated or incorrect #include directives
    and replaces them with the correct equivalents.

    Currently uses an empty replacement table — extend HEADER_REPLACEMENTS above
    to add project-specific fixes.

    Args:
        code (str): Raw C source code string.

    Returns:
        str: Code with any matched headers replaced.
    """
    if not code:
        return code

    for old_header, new_header in HEADER_REPLACEMENTS.items():
        if old_header in code:
            logger.info(f"Replacing header '{old_header}' with '{new_header}'")
            code = code.replace(old_header, new_header)

    return code
