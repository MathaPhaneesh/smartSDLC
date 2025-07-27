# SmartSDLC - AI-Enhanced Software Development Platform (Vercel Ready)

SmartSDLC is a modern, AI-powered software development platform that streamlines requirements analysis, code generation, test creation, and developer assistance—all deployable as a serverless app on Vercel.

---

## 🚀 Project Structure

```
/api/                        # Python serverless functions (each file = one endpoint)
    analyze-requirements.py  # Requirements analysis endpoint
    generate-code.py         # Code generation endpoint
    generate-tests.py        # Test generation endpoint
    chat.py                  # AI chat assistant endpoint
    utils.py                 # Shared config and OpenRouter API logic
index.html                   # Main frontend UI (now in project root)
favicon.png                  # Favicon (now in project root)
requirements.txt             # Python dependencies
vercel.json                  # Vercel routing/build config
README.md
LICENSE
```

---

## 🌐 Live Deployment on Vercel

1. **Install Vercel CLI:**
   ```sh
   npm i -g vercel
   ```
2. **Deploy:**
   ```sh
   vercel
   ```
   - Follow the prompts.
   - Set your environment variables (see below) in the Vercel dashboard after the first deploy.

---

## ⚙️ Environment Variables
Set these in your Vercel project dashboard:
- `OPENROUTER_API_KEY` — Your OpenRouter API key

---

## 🛠️ Features

- **Requirements Analysis:** Upload a PDF or enter text to extract functional, non-functional, and technical requirements, plus user stories.
- **AI Code Generation:** Generate code in your chosen language and framework from natural language prompts.
- **Test Case Generation:** Instantly create unit, integration, or end-to-end tests for your code.
- **Development Assistant Chat:** Get AI-powered help with code, architecture, debugging, and best practices.

---

## 📡 API Endpoints
All endpoints are POST and accept form data.

| Endpoint                    | Description                                 |
|----------------------------|---------------------------------------------|
| `/api/analyze-requirements` | Analyze requirements from PDF or text input |
| `/api/generate-code`        | Generate code from prompt and language      |
| `/api/generate-tests`       | Generate tests for code in a language       |
| `/api/chat`                 | Chat with the AI development assistant      |

All endpoints use FastAPI and share OpenRouter API logic from `/api/utils.py`.

---

## 🧩 Shared Logic: `/api/utils.py`
- Loads environment variables
- Stores model names and OpenRouter API URL
- Provides `call_openrouter_api()` for all endpoints

---

## 📦 Dependencies
See `requirements.txt`:
```
fastapi
uvicorn[standard]
python-multipart
requests
aiofiles
PyPDF2
jinja2
```

---

## 📝 Static Files
- `index.html` — Main frontend UI (now in project root)
- `favicon.png` — Favicon (now in project root)

---

## ❌ Security & Rate Limiting
- **No authentication or JWT**: All endpoints are public (add auth if needed)
- **No slowapi/rate limiting**: Vercel serverless does not support Python background state
- **CORS**: Not needed for static+API on same domain

---

## 🏁 Quickstart (Local Dev)
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env` with your OpenRouter API key
4. Run any endpoint locally with Uvicorn for testing, e.g.:
   ```sh
   uvicorn api.chat:app --reload
   ```
5. Open `index.html` in your browser for the frontend

---

## 📄 License
MIT License — see LICENSE file.

---

## 🙋‍♂️ Support
Open an issue or PR on GitHub for help or contributions. 