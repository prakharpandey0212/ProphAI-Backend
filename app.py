# --- INSTALLATION INSTRUCTIONS (These are comments, not code) ---
# 1. Activate Virtual Environment (venv)
# 2. pip install fastapi uvicorn pydantic google-genai
# 3. Server run karne ke liye: uvicorn app:app --reload
# -----------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import asyncio 
from google import genai
from google.genai.errors import APIError

# --- IMPORTANT: SETUP & SECURITY (FIXED) ---
# Code ab GEMINI_API_KEY ko environment se load karega.
API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY:
    print("CRITICAL: GEMINI_API_KEY environment variable not set. Application will fail on deployment.")

# Initialize FastAPI App
app = FastAPI(title="ProphAI Backend")

# Configure CORS (NO CHANGE)
origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response data models (Pydantic)
class IdeaRequest(BaseModel):
    idea: str

class TechStackDetail(BaseModel):
    component: str
    technology: str
    justification: str

class CompetitorDetail(BaseModel):
    competitor: str
    similarFeatures: str
    differentiation: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class AnalysisResult(BaseModel):
    noveltyScore: int
    trendsScore: int
    viralityPotential: int
    netWorthEstimate: str
    uniquenessSummary: str
    longTermViability: str
    ecosystemRisks: str
    adoptionDrivers: str
    actionableNextSteps: list[str]
    keywords: list[str]
    techAppeal: str
    techStack: list[TechStackDetail]
    projectPhases: list[dict] 
    competitiveLandscape: list[CompetitorDetail]

# --- AI Prompt Logic (Integrated Validation) ---
def create_analysis_prompt(idea: str) -> str:
    return f"""
    You are ProphAI, the Strategic Innovation Core. Your primary task is to **first validate** whether the following input describes a software project, product, or clear technological innovation.
    Input Idea: "{idea}"
    **--- CRITICAL INSTRUCTION ---**
    **CONDITION A (Invalid/Non-Project):** If the input is a general question (e.g., "What is AI?"), a single irrelevant word, or does NOT describe a product/innovation, you MUST return a strict JSON response where **noveltyScore is 0** and ALL scores (trendsScore, viralityPotential) are **0** (zero).
    * Use this specific error summary for general questions/irrelevant input: **"Please input a valid project or innovation in proper manner."**
    * Use this specific error summary if the input is vague but might pass the length check: **"No project described below."**
    * For Condition A, fill all descriptive fields (e.g., netWorthEstimate, viability) with **"N/A: Input Validation Failed"** and use placeholder lists with error messages.
    **CONDITION B (Valid Project):** If the input clearly describes a software project or innovation, proceed with the full professional analysis and provide realistic scores (0-100) and detailed descriptions.
    **REQUIRED JSON STRUCTURE (Strictly adhere to this format for both CONDITIONS A and B):**
    
    {{
        "noveltyScore": [Integer 0-100],
        "trendsScore": [Integer 0-100],
        "viralityPotential": [Integer 0-100],
        "netWorthEstimate": "String describing the 3-year valuation range (e.g., '₹5 Crore - ₹10 Crore (High Tech Value)' OR 'ZERO - Input Not Validated')",
        "uniquenessSummary": "A concise summary of the core product's USP, OR the specific error message from Condition A.",
        "longTermViability": "A concise assessment of the idea's resilience, OR 'N/A: Invalid Input'.",
        "ecosystemRisks": "Concise summary of 2-3 risks, OR 'N/A: Invalid Input'.",
        "adoptionDrivers": "Concise summary of 2-3 drivers, OR 'N/A: Invalid Input'.",
        "actionableNextSteps": [
            "1. (Practical Step or Error Message from Condition A)",
            "2. (Practical Step or Error Message from Condition A)",
            "3. (Practical Step or Error Message from Condition A)"
        ],
        "keywords": [
            "Validation_Error", 
            "Invalid_Input"
        ],
        "techAppeal": "A concise summary of the project's appeal, OR 'N/A: Invalid Input'.",
        "techStack": [
            {{"component": "Frontend/UI", "technology": "React/Next.js", "justification": "Modern, scalable component-based architecture."}},
            {{"component": "Backend/API", "technology": "FastAPI/GoLang", "justification": "High performance and asynchronous handling for real-time data."}},
            {{"component": "Database/Data Layer", "technology": "PostgreSQL/VectorDB", "justification": "Structured data and efficient vector search for AI embeddings."}}
        ],
        "projectPhases": [
            {{"phase": "Phase 1: Proof of Concept", "duration": "4 Weeks", "focus": "Core Logic & Data Integrity, Minimal UI."}},
            {{"phase": "Phase 2: Alpha Launch", "duration": "8 Weeks", "focus": "Complete MVP, Security Audit, Internal Testing."}}
        ],
        "competitiveLandscape": [
            {{"competitor": "Major Competitor A", "similarFeatures": "AI-driven content generation.", "differentiation": "Your niche focus."}},
            {{"competitor": "Niche Startup B", "similarFeatures": "Simple UI.", "differentiation": "Superior security."}}
        ]
    }}
    """

# --- API Endpoint (ANALYZE) ---
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_project(request: IdeaRequest):
    # 1. Fallback data definition
    default_data = {
        "noveltyScore": 60, "trendsScore": 65, "viralityPotential": 45,
        "netWorthEstimate": "₹1 Crore - ₹2 Crore (System Fallback)", 
        "uniquenessSummary": "Could not connect to Analysis Core. Returning low-confidence base analysis. Check API Key.",
        "longTermViability": "Uncertain (Core failure prevented deep analysis).",
        "ecosystemRisks": "Check your API key and network connection.",
        "adoptionDrivers": "Try running the server again with correct key.",
        "actionableNextSteps": [
            "1. Verify the 'API_KEY' is set correctly in environment.",
            "2. Check FastAPI logs for detailed error trace and JSON format errors.",
            "3. Re-run 'uvicorn app:app --reload'."
        ],
        "keywords": ["Fallback", "System Error", "Check Key"],
        "techAppeal": "Fallback analysis: Cannot determine true technical appeal.",
        "techStack": [{"component": "System", "technology": "N/A", "justification": "Failure to connect to core AI."}],
        "projectPhases": [{"phase": "Error Phase", "duration": "N/A", "focus": "Troubleshoot Server Connection."}],
        "competitiveLandscape": [{"competitor": "System Fallback", "similarFeatures": "N/A", "differentiation": "Connection Error"}] 
    }

    try:
        # 2. API call and response processing
        if not API_KEY:
            raise APIError("Gemini API Key is not set in environment variables.")

        client = genai.Client(api_key=API_KEY) 
        prompt = create_analysis_prompt(request.idea)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        analysis_data = json.loads(response.text)
        
        # 3. FIX: List to String conversion for Pydantic validation
        if isinstance(analysis_data.get('ecosystemRisks'), list):
            analysis_data['ecosystemRisks'] = ' '.join(analysis_data['ecosystemRisks'])
        if isinstance(analysis_data.get('adoptionDrivers'), list):
            analysis_data['adoptionDrivers'] = ' '.join(analysis_data['adoptionDrivers'])
        
        # 4. Successful data return
        return AnalysisResult(**analysis_data)

    except (APIError, json.JSONDecodeError, ValueError) as e:
        # 5. AI/JSON/Pydantic validation error fallback
        print(f"Analysis Error (API/JSON/Validation): {e}")
        asyncio.sleep(1) 
        return default_data 
        
    except Exception as e:
        # 6. General error handling
        print(f"Internal Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")

# ----------------------------------------------------
# 💬 NEW CHATBOT ENDPOINT (for general questions)
# ----------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    chat_prompt = f"""
    You are a friendly and knowledgeable technical assistant. Answer the user's question concisely. 
    If the question is about a project or innovation analysis, gently redirect them to use the main ProphAI form.
    User Question: {request.message}
    """
    try:
        if not API_KEY:
            raise APIError("Gemini API Key is not set in environment variables.")
            
        client = genai.Client(api_key=API_KEY)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=chat_prompt,
        )
        
        return ChatResponse(reply=response.text)

    except Exception as e:
        print(f"Chat Error: {e}")
        return ChatResponse(reply="Sorry, I can't connect to the chat service right now.")