import re
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_json_block_from_response(text: str) -> str:
    """
    Extract JSON block from markdown-style ```json ... ``` even if the object starts on the next line.
    Falls back to returning the entire string.
    """
    try:
        logger.info("🔍 Trying to extract JSON block from text...")
        match = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            logger.info("✅ JSON block found inside ```json wrapper.")
            return match.group(1).strip()
        else:
            logger.warning("⚠️ No ```json wrapper found. Using full text as fallback.")
            return text.strip()
    except Exception as e:
        logger.error(f"❌ Exception while extracting JSON block: {e}")
        return text.strip()


def extract_c_code_from_output(output_field: str) -> str:
    """
    Extract C code from markdown-style ```c ... ``` block inside the 'output' field.
    Falls back to returning the output content directly.
    """
    try:
        logger.info("🔍 Trying to extract ```c block from output field...")
        match = re.search(r"```c\s*\n(.*?)\n```", output_field, re.DOTALL)
        if match:
            logger.info("✅ C code block extracted.")
            return match.group(1).strip()
        else:
            logger.warning("⚠️ No ```c block found. Using raw output.")
            return output_field.strip()
    except Exception as e:
        logger.error(f"❌ Exception while extracting C code: {e}")
        return output_field.strip()


def extract_code(text: str) -> str:
    """
    Main driver: extract clean C code from full LLM response text.
    1. Extract JSON (possibly wrapped)
    2. Parse JSON
    3. Extract 'output' field and strip any ```c blocks
    """
    try:
        logger.info("🚀 Starting full code extraction pipeline.")
        json_str = extract_json_block_from_response(text)

        parsed = json.loads(json_str)
        logger.info("✅ JSON successfully parsed.")

        if isinstance(parsed, list):
            logger.info("ℹ️ JSON is a list — unwrapping first object.")
            parsed = parsed[0]

        output = parsed.get("output", "")
        if not output:
            logger.warning("⚠️ 'output' field is empty or missing.")

        code = extract_c_code_from_output(output)
        logger.info("✅ Final code extracted.")
        return code

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in extract_code: {e}")
    
    return None
