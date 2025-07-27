from fastapi import FastAPI, Form, HTTPException
import os
import requests

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = {
    "chat": "gpt-4o-mini"
}

def call_openrouter_api(model: str, prompt: str, system_prompt: str = "") -> dict:
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app.vercel.app/"
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
                error_msg += f" - {error_detail}"
            except:
                if response.text:
                    error_msg += f" - {response.text}"
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/chat")
async def chat(message: str = Form(...)):
    system_prompt = """You are an AI development assistant. Help users with:\n• Software development best practices\n• Code review and suggestions\n• Debugging assistance\n• Architecture recommendations\n• General programming questions\n\nProvide clear, concise, and practical advice.\nUse bullet points (•) for lists and formatting."""
    return call_openrouter_api(MODELS["chat"], message, system_prompt) 