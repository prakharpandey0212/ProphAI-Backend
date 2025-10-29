from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import asyncio 
from google import genai
from google.genai.errors import APIError

# --- IMPORTANT: SETUP & SECURITY (NO CHANGE) ---
API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set. Using hardcoded fallback key for execution.") 
    API_KEY = "AIzaSyCX4XNnhSmFbjK3dUv4B_1dd5qBcVIBds8" 


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

# 🌟 Naya model for Competition
class CompetitorDetail(BaseModel):
    competitor: str
    similarFeatures: str
    differentiation: str

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
# Main fix: AI ko hi validation karne ka kaam diya gaya hai.
def create_analysis_prompt(idea: str) -> str:
    return f"""
    You are ProphAI, the Strategic Innovation Core. Your primary task is to **first validate** whether the following input describes a software project, product, or clear technological innovation.

    Input Idea: "{idea}"

    **--- CRITICAL INSTRUCTION ---**

    **CONDITION A (Invalid/Non-Project):** If the input is a general question (e.g., "What is AI?"), a single irrelevant word, or does NOT describe a product/innovation, you MUST return a strict JSON response where **noveltyScore is 0** and ALL scores (trendsScore, viralityPotential) are **0** (zero).
    
    * Use this specific error summary for general questions/irrelevant input: **"Please input a valid project or innovation in proper manner."**
    * Use this specific error summary if the input is vague but might pass the length check: **"No project described below."**
    * For Condition A, fill all descriptive fields (e.g., netWorthEstimate, viability) with **"N/A: Input Validation Failed"** and use placeholder lists.

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
            "1. (Step or Error Message from Condition A)",
            "2. (Step or Error Message from Condition A)",
            "3. (Step or Error Message from Condition A)"
        ],
        "keywords": [
            "Validation_Error", 
            "Invalid_Input"
        ],
        "techAppeal": "A concise summary of the project's appeal, OR 'N/A: Invalid Input'.",
        
        "techStack": [
            {{"component": "Frontend/UI", "technology": "React/Next.js", "justification": "Modern, scalable component-based architecture."}}
        ],

        "projectPhases": [
            {{"phase": "Phase 1: Proof of Concept", "duration": "4 Weeks", "focus": "Core Logic & Data Integrity, Minimal UI."}}
        ],
        
        "competitiveLandscape": [
            {{"competitor": "Major Competitor A", "similarFeatures": "AI-driven content generation.", "differentiation": "Your niche focus."}}
        ]
    }}
    """

# --- API Endpoint (LOGIC CORRECTED) ---
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_project(request: IdeaRequest):
    # 1. Fallback data ko 'try' block se pehle define karna
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
        # 2. API call aur response processing
        client = genai.Client(api_key=API_KEY) 
        prompt = create_analysis_prompt(request.idea) # Updated prompt call

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        # 3. JSON load karna
        analysis_data = json.loads(response.text)
        
        # 4. FIX: List to String conversion for Pydantic validation (Bura AI output fix karne ke liye)
        if isinstance(analysis_data.get('ecosystemRisks'), list):
            analysis_data['ecosystemRisks'] = ' '.join(analysis_data['ecosystemRisks'])
        if isinstance(analysis_data.get('adoptionDrivers'), list):
            analysis_data['adoptionDrivers'] = ' '.join(analysis_data['adoptionDrivers'])
        
        # 5. Successful data return
        return AnalysisResult(**analysis_data)

    except (APIError, json.JSONDecodeError, ValueError) as e:
        # 6. AI/JSON/Pydantic validation error hone par default_data return hoga.
        print(f"Analysis Error (API/JSON/Validation): {e}")
        await asyncio.sleep(1) 
        return default_data 
        
    except Exception as e:
        # 7. Koi bhi doosra unexpected error hone par HTTPException raise hoga.
        print(f"Internal Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")