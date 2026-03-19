# Necassary Library Imports
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import necassary configuration parameters
from config.model import BASE_DELAY

API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your Gemini API key
# Set API URL template
API_URL_TEMPLATE = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def call_gemini_api(prompt: str, temperature: float = 0.7, retry_count: int = 0) -> str | None:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "topP": 0.8,
            "topK": 40
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    try:
        response = requests.post(API_URL_TEMPLATE, headers=headers, json=payload)

        if response.status_code == 200:
            time.sleep(BASE_DELAY)
            content = response.json()
            if "candidates" in content:
                return content["candidates"][0]["content"]["parts"][0]["text"]

        elif response.status_code == 429:
            wait_time = 5 # Optional backoff
            logger.warning(f"429 Too Many Requests — sleeping {wait_time}s and retrying...")
            time.sleep(wait_time)
            return call_gemini_api(prompt, temperature, retry_count + 1)

        else:
            logger.error(f"API Error {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Exception during API call: {str(e)}")

