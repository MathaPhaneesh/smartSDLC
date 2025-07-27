from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import os
import requests
import io
import PyPDF2

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = {
    "requirements": "gpt-4o-mini"
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

@app.post("/api/analyze-requirements")
async def analyze_requirements(file: UploadFile = File(None), text: str = Form(None)):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Either file or text must be provided")
    content = ""
    if file:
        if file.content_type == "application/pdf":
            try:
                file_content = await file.read()
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
    else:
        content = text if text is not None else ""
    if not content.strip():
        raise HTTPException(status_code=400, detail="No content provided for analysis")
    system_prompt = """You are a requirements analysis expert. Analyze the given text and extract software requirements.\n\nFormat your response as:\n\n**PROJECT REQUIREMENTS ANALYSIS**\n\n**1. Functional Requirements:**\n• [List key functional requirements]\n\n**2. Non-Functional Requirements:**\n• [List performance, security, usability requirements]\n\n**3. Technical Requirements:**\n• [List technology stack, framework requirements]\n\n**4. User Stories:**\n• [List key user stories in format: As a [user], I want [feature] so that [benefit]]\n\nKeep each point concise and actionable."""
    return call_openrouter_api(MODELS["requirements"], content, system_prompt) 