import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv
import json

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = {
    "requirements": "mistralai/mistral-7b-instruct",
    "code": "deepseek/deepseek-coder",
    "tests": "deepseek/deepseek-coder",
    "chat": "meta-llama/llama-3-8b-instruct"
}

def call_openrouter_api(model: str, prompt: str, system_prompt: str = "") -> dict:
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8080"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    data = {"model": model, "messages": messages}
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return {"response": result["choices"][0]["message"]["content"]}
    except requests.exceptions.RequestException as e:
        error_msg = f"OpenRouter API error: {str(e)}"
        if response is not None:
            try:
                error_detail = response.json()
                error_msg += f" - {json.dumps(error_detail)}"
            except:
                if response.text:
                    error_msg += f" - {response.text}"
        raise HTTPException(status_code=500, detail=error_msg) 