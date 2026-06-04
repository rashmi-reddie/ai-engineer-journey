# """
# WEEK 1 CAPSTONE: AI Resume Analyzer
# =====================================
# What it does:
#   - User pastes their resume text
#   - User pastes a job description
#   - AI analyzes match score (0-100)
#   - AI returns: strengths, gaps, improvements, keywords missing

# Tech used (everything from Week 1):
#   - Python classes (Day 4)
#   - FastAPI backend with 2 endpoints (Day 3)
#   - Streamlit frontend (Day 2)
#   - Prompt engineering with structured output (Day 5)
#   - Error handling (Day 4)
#   - JSON response parsing (Day 4)

# Endpoints:
#   POST /analyze  - takes resume + job_description, returns analysis
#   GET /health    - health check

# Files:
#   resume_analyzer.py  - core analysis logic (class)
#   resume_api.py       - FastAPI backend
#   resume_app.py       - Streamlit frontend
# """

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

ANALYSIS_PROMPT="""You are an expert technical recruiter and career caoch with 10 years of experience in hiring AI Engineers and software developers in India.

Analyse this resume against the job description and return only a valid JSON object with no markdown, no backticks, no extra text - just the raw JSON.

JSON structure:
{{
   "match_score" : ,
   "summary": "<2 sentence overall assessment>",
   "strengths":["","",""],
   "gaps":["","",""],
   "missing_keywords" : ["",""],
   "improvements":[
       "",
       "",
       ""],
       "interview_likelihood":"",
       "one_line_verdict":""}}
RESUME:
{resume}

JOB DESCRIPTION:
{job_description}
       """

class ResumeAnalyzer:
    def __init__(self):
        self.client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.config=types.GenerateContentConfig(
            temperature=0.3
        )
        
    def analyze(self,resume_text,job_description):
        if len(resume_text.strip()) < 50:
            raise ValueError("Resume text is too short. Please paste your full resume.")
        if len(job_description.strip()) < 30:
            raise ValueError("Job description is too short.")
        
        prompt=ANALYSIS_PROMPT.format(
            resume=resume_text,
            job_description=job_description
        )
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=self.config,
            contents=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        )
        raw=response.text.strip()
        raw=raw.replace("```json","").replace("```","").strip()
        
        try:
            result=json.loads(raw)
            return result
        except json.JSONDecodeEroor:
            return{
                "match_score":0,
                "summary":"Analysis failed - could not parse response.",
                "raw_response":raw,
                "error": "JSON parse failed"
            }
            
    def get_score_label(self,score):
        if score >= 80: return "Strong match"
        if score >= 60: return "Good match"
        if score >= 40: return "Partial match"
        return "Weak match"

if __name__=="__main__":
    analyzer=ResumeAnalyzer()
    test_resume="""
    Rashmitha - BTech Computer Science 2025
    Skills: Python,JavaScript,React, basic ML
    Projects: built a chatbot using Gemini API, FastAPI backend
    Education: BTech CSE, 9.37 CGPA
    """
    
    test_jd="""
    AI Engineer - 0-2 years experience
    Requirements : Python, FastAPI,LLMs, REST APIs, Git
    Nice to have: LangChain,vector databases, Streamlit
    """
    result=analyzer.analyze(test_resume,test_jd)
    print(json.dumps(result,indent=2))
    
    