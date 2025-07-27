import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Model configurations - Using correct model names for OpenRouter
MODELS = {
    "requirements": "mistralai/mistral-7b-instruct",
    "code": "deepseek/deepseek-coder",
    "tests": "deepseek/deepseek-coder",
    "chat": "meta-llama/llama-3-8b-instruct"
}

# API Settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "SmartSDLC"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 8 days

# OpenRouter Settings
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"