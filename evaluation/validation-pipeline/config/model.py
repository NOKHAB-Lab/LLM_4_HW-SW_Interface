from pathlib import Path

# 🌀 Decide for RPI Mode
RPI_PICO = False

MAX_RETRIES = 3

# Rate limiting settings
BASE_DELAY = 1  # Base delay between API calls in seconds
JITTER = 1      # Random jitter to add to delay (up to this many seconds)
MAX_REQUESTS_PER_MINUTE = 100  # Maximum requests per minute to avoid rate limiting

# You can inject API keys externally or load from config
API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your Gemini API key

#BASE_DIR = f"D:/Personal/SDU/LLM - Thesis/Progress/Week 12/Data Pipeline/Phase 2/"
BASE_DIR = Path(__file__).resolve().parent.parent