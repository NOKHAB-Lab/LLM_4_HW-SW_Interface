# Important Library and Function Imports
import logging
from .gemini_api import call_gemini_api

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_api_connection():
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