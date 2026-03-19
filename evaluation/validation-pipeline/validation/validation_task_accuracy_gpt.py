# Imports 
import re
from api.gpt_api import call_gpt_api
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Functions

# Evaluate Task Correctness
def prepare_and_rate_sample_gpt(task_description, generated_code):
    prompt = f"""Given the following task:
{task_description}

And the following generated C code:
{generated_code}

Please calculate how accurately the code meets the task requirements, expressed as a percentage from 0% to 100%, 
where 100% means a perfect match. Only respond with a single number followed by a percent sign, e.g., "92%"."""
    
    response = call_gpt_api(prompt)
    #write_to_txt('gpt_correct.txt', response)
    if response:
        logger.debug(f"Processing GPT response of Code Correctness: '{response.strip()}'")
        match = re.search(r'(\b|[^0-9])?([1-9]?[0-9]|100)%(\b|[^0-9])?', response.strip())
        if match and match.group(2):
            percentage = int(match.group(2))
            if 0 <= percentage <= 100:
                return percentage
            else:
                logger.warning(f"Extracted percentage '{percentage}' out of range [0-100], returning None")
                return None
        else:
            logger.info("No valid percentage found in GPT response of Code Task Correctness.")
            return None
    else:
        logger.error("No response from API.")
        return None


def compare_and_rate_inferred_code_gpt(task_description, inferred_code, valid_code):
    prompt = f"""Given the following task:
{task_description}

Here is the valid working C code that correctly fulfills the task:
{valid_code}

Here is the inferred/generated C code:
{inferred_code}

Evaluate how closely the inferred code matches the valid code in terms of fulfilling the task requirements,
correctness, and functionality. Express the similarity as a percentage from 0% to 100%, where 100% means functionally identical.

Only respond with a single number followed by a percent sign, e.g., "85%"."""
    
    response = call_gpt_api(prompt)
    #write_to_txt('gpt_compare.txt', response)
    if response:
        logger.debug(f"Processing GPT response of Code Comparison: '{response.strip()}'")
        match = re.search(r'(\b|[^0-9])?([1-9]?[0-9]|100)%(\b|[^0-9])?', response.strip())
        if match and match.group(2):
            percentage = int(match.group(2))
            if 0 <= percentage <= 100:
                return percentage
            else:
                logger.warning(f"Extracted percentage '{percentage}' out of range [0-100], returning None")
                return None
        else:
            logger.info("No valid percentage found in GPT response of Code Comparison.")
            return None
    else:
        logger.error("No response from API.")
        return None

def write_to_txt(file_path: str, data: str) -> bool:
    """
    Create a new text file and write data to it, overwriting any existing content.
    
    Args:
        file_path (str): Path to the text file.
        data (str): Data to write to the file.
    
    Returns:
        bool: True if write was successful, False otherwise.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
            if not data.endswith('\n'):  # Ensure each entry ends with a newline
                f.write('\n')
        logger.debug(f"Successfully wrote data to {file_path}")
        return True
    except PermissionError:
        logger.error(f"Permission denied writing to {file_path}")
        return False
    except OSError as e:
        logger.error(f"Error writing to {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error writing to {file_path}: {e}")
        return False