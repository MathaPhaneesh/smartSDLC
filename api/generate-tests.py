from fastapi import FastAPI, Form, HTTPException
import os
import requests

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = {
    "tests": "gpt-4o-mini"
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

@app.post("/api/generate-tests")
async def generate_tests(code: str = Form(...), language: str = Form(...), test_type: str = Form("unit")):
    system_prompt = f"""You are a testing expert. Generate {test_type} tests for the following {language} code.\n\nInclude:\n- Test setup and teardown\n- Test cases with clear descriptions\n- Appropriate assertions\n- Edge cases and error conditions\n\nUse the standard testing framework for {language}."""
    return call_openrouter_api(MODELS["tests"], code, system_prompt) 