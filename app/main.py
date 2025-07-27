from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import requests
import os
from dotenv import load_dotenv
from typing import Optional
import PyPDF2
import io
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="SmartSDLC",
    description="""
    SmartSDLC - AI-Enhanced Software Development Platform
    
    Features:
    - PDF/Prompt-Based Requirement Analysis
    - AI Code Generation
    - Test Case Generation
    - Development Assistant Chat
    
    This API provides endpoints for automated software development tasks using AI.
    """,
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Model configurations
MODELS = {
    "requirements": "meta-llama/llama-3-8b-instruct",
    "code": "meta-llama/llama-3-8b-instruct",
    "tests": "meta-llama/llama-3-8b-instruct", 
    "chat": "meta-llama/llama-3-8b-instruct"
}

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="SmartSDLC API",
        version="1.0.0",
        description="""
        SmartSDLC - AI-Enhanced Software Development Platform
        
        Features:
        - PDF/Prompt-Based Requirement Analysis
        - AI Code Generation
        - Test Case Generation
        - Development Assistant Chat
        
        This API provides endpoints for automated software development tasks using AI.
        """,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze-requirements")
@limiter.limit("10/minute")
async def analyze_requirements(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Analyze software requirements from PDF or text input.
    
    Parameters:
    - file: PDF file containing requirements (optional)
    - text: Text input containing requirements (optional)
    
    Returns:
    - Structured analysis of requirements including functional, non-functional, and technical requirements
    """
    try:
        if not file and not text:
            raise HTTPException(status_code=400, detail="Either file or text must be provided")
        
        content = ""
        if file:
            # Handle PDF file
            if file.content_type == "application/pdf":
                try:
                    file_content = await file.read()
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    content = ""
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
                except Exception as e:
                    print(f"Error reading PDF: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Only PDF files are supported")
        else:
            content = text if text is not None else ""
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="No content provided for analysis")
        
        system_prompt = """You are a requirements analysis expert. Analyze the given text and extract software requirements.
        
        Format your response as:
        
        **PROJECT REQUIREMENTS ANALYSIS**
        
        **1. Functional Requirements:**
        • [List key functional requirements]
        
        **2. Non-Functional Requirements:**
        • [List performance, security, usability requirements]
        
        **3. Technical Requirements:**
        • [List technology stack, framework requirements]
        
        **4. User Stories:**
        • [List key user stories in format: As a [user], I want [feature] so that [benefit]]
        
        Keep each point concise and actionable."""
        
        response = await call_openrouter_api(MODELS["requirements"], content, system_prompt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-code")
@limiter.limit("10/minute")
async def generate_code(
    request: Request,
    prompt: str = Form(...),
    language: str = Form(...),
    framework: Optional[str] = Form(None)
):
    """
    Generate code based on the provided prompt and specifications.
    
    Parameters:
    - prompt: Description of the code to generate
    - language: Programming language to use
    - framework: Optional framework to use
    
    Returns:
    - Generated code with comments and documentation
    """
    try:
        system_prompt = f"""You are an expert {language} developer. Generate code based on the following requirements.
        
        If a framework is specified, use best practices for that framework.
        Include appropriate comments and documentation.
        Ensure the code is production-ready and follows best practices."""
        
        full_prompt = f"Framework: {framework}\n\nRequirements: {prompt}" if framework else prompt
        response = await call_openrouter_api(MODELS["code"], full_prompt, system_prompt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-tests")
@limiter.limit("10/minute")
async def generate_tests(
    request: Request,
    code: str = Form(...),
    language: str = Form(...),
    test_type: str = Form("unit")
):
    """
    Generate test cases for the provided code.
    
    Parameters:
    - code: The code to generate tests for
    - language: Programming language of the code
    - test_type: Type of tests to generate (unit, integration, e2e)
    
    Returns:
    - Generated test cases with setup and assertions
    """
    try:
        system_prompt = f"""You are a testing expert. Generate {test_type} tests for the following {language} code.
        
        Include:
        - Test setup and teardown
        - Test cases with clear descriptions
        - Appropriate assertions
        - Edge cases and error conditions
        
        Use the standard testing framework for {language}."""
        
        response = await call_openrouter_api(MODELS["tests"], code, system_prompt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
@limiter.limit("20/minute")
async def chat(
    request: Request,
    message: str = Form(...)
):
    """
    Chat with the AI development assistant.
    
    Parameters:
    - message: The user's message
    
    Returns:
    - AI assistant's response
    (No authentication required)
    """
    try:
        system_prompt = """You are an AI development assistant. Help users with:
        • Software development best practices
        • Code review and suggestions
        • Debugging assistance
        • Architecture recommendations
        • General programming questions
        
        Provide clear, concise, and practical advice.
        Use bullet points (•) for lists and formatting."""
        
        response = await call_openrouter_api(MODELS["chat"], message, system_prompt)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def call_openrouter_api(model: str, prompt: str, system_prompt: str = "") -> dict:
    """Call OpenRouter API with the given model and prompt."""
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API key not configured"
        )
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8080"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model,
        "messages": messages
    }
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)