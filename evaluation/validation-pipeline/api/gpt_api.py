# Necessary Library Imports
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Your custom GPT API settings
API_URL = "https://api.openai.com/v1/chat/completions"  # Change this to your actual endpoint
API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI API key

def call_gpt_api(prompt: str, temperature: float = 0.7, model: str = "gpt-4o") -> str | None:
    headers = {
        "Content-Type": "application/json",
       "Authorization": f"Bearer {API_KEY}",  # Uncomment if your API requires it
    }

    payload = {
        "model": model,  # Update if your model has a different ID
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "top_p": 0.95,
        "n": 1,
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            content = response.json()
            return content['choices'][0]['message']['content']
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            if response.status_code == 429:
                logger.warning("429 Too Many Requests — retrying after delay")
                time.sleep(5)
    except Exception as e:
        logger.error(f"Exception during API call: {str(e)}")

    return None
