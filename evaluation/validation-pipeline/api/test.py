# Important Library and Function Imports
import logging
from .gemini_api import call_gemini_api
from .gpt_api import call_gpt_api

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_gemini_api_connection():
    """Test the API connection before starting the main process."""
    logger.info("Testing connection to Gemini API...")
    
    test_prompt = "Write a single line of C code that prints 'Hello World'"
    response = call_gemini_api(test_prompt, temperature=0.1)
    
    if response:
        logger.info("✅ API connection successful")
        return True
    else:
        logger.error("❌ API connection failed. Please check your API key and internet connection.")
        return False
    
def test_gpt_api_connection():
    """Test the API connection before starting the main process."""
    logger.info("Testing connection to GPT API...")
    
    test_prompt = "Write a single line of C code that prints 'Hello World'"
    response = call_gpt_api(test_prompt, temperature=0.1)
    
    if response:
        logger.info("✅ API connection successful")
        return True
    else:
        logger.error("❌ API connection failed. Please check your API key and internet connection.")
        return False