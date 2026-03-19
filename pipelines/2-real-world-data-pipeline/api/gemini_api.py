# Necassary Library Imports
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import necassary configuration parameters
from config.model import BASE_DELAY, MAX_REQUESTS_PER_MINUTE, API_KEYS

# Set API URL template
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

# Rate limiting trackers
api_key_index = 0
api_call_times = {i: [] for i in range(len(API_KEYS))}

def rotate_api_key() -> tuple[str, int]:
    global api_key_index
    key = API_KEYS[api_key_index]
    index = api_key_index
    api_key_index = (api_key_index + 1) % len(API_KEYS)
    return key, index

def manage_api_rate(index: int):
    now = time.time()
    times = api_call_times[index]
    times = [t for t in times if now - t < 60]  # Keep only the last 60 seconds
    api_call_times[index] = times

    if len(times) >= MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (now - times[0]) + 1
        logger.info(f"[KEY {index}] Rate limit hit. Waiting {wait_time:.2f}s")
        time.sleep(wait_time)

def call_gemini_api(prompt: str, temperature: float = 0.7) -> str | None:
    api_key, key_index = rotate_api_key()
    manage_api_rate(key_index)

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

    url = API_URL_TEMPLATE.format(api_key=api_key)

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            api_call_times[key_index].append(time.time())
            content = response.json()
            if "candidates" in content:
                return content["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"[KEY {key_index}] API Error {response.status_code}: {response.text}")
            if response.status_code == 429:
                logger.warning("429 Too Many Requests: applying long delay")
                time.sleep(BASE_DELAY * 5)

    except Exception as e:
        logger.error(f"Exception during API call: {str(e)}")

    return None
