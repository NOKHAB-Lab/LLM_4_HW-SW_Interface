from pathlib import Path

# 🌀 Decide for RPI Mode
RPI_PICO: bool = False

MAX_RETRIES = 3

# Rate limiting settings
BASE_DELAY = 5  # Base delay between API calls in seconds
JITTER = 2      # Random jitter to add to delay (up to this many seconds)
MAX_REQUESTS_PER_MINUTE = 15  # Maximum requests per minute to avoid rate limiting

# You can inject API keys externally or load from config
API_KEYS = [
    "YOUR_GEMINI_API_KEY_1",  # Replace with your Gemini API key
    "YOUR_GEMINI_API_KEY_2",  # Optional: add more keys for rotation
    "YOUR_GEMINI_API_KEY_3"   # Optional: add more keys for rotation
    # Add more as needed
]

#BASE_DIR = f"D:/Personal/SDU/LLM - Thesis/Progress/Week 12/Data Pipeline/Phase 2/"
BASE_DIR = Path(__file__).resolve().parent.parent

BUILD_AND_SYNTAX_VALIDATTION: bool = False