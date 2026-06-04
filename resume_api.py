from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from resume_analyzer import ResumeAnalyzer

app=FastAPI(title="Resume Analyzer API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])
analyzer=ResumeAnalyzer()

class AnalyzeRequest(BaseModel):
    resume: str
    job_description: str

@app.get("/health")
def health():
    return {"status":"ok", "service": "Resume Analyzer"}

@app.post("/analyze")
def analyze_resume(request: AnalyzeRequest):
    try:
        result=analyzer.analyze(request.resume,request.job_description)
        result["score_label"]=analyzer.get_score_label(
            result.get("match_score",0)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))