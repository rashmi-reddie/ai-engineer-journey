import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import RAGEngine

app=FastAPI(title="RAG Document Q&A API")
app.add_middleware(CORSMiddleware,allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])

engine=RAGEngine()
UPLOAD_DIR="./upload_docs"
os.makedirs(UPLOAD_DIR,exist_ok=True)

class QuestionRequest(BaseModel):
    question:str
    n_results:int=4
    
class TextRequest(BaseModel):
    text:str
    source_name: str="pasted_text"
    
@app.get("/")
def root():
    return {"message": "RAG Q&A API running", "stats": engine.get_stats()}
@app.post("/upload")
async def upload_pdf(file: UploadFile=File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400,"Only PDF Files are supported.")
    filepath=os.path.join(UPLOAD_DIR,file.filename)
    with open(filepath,"wb") as f:
        shutil.copyfileobj(file.file,f)
    try:
        chunks=engine.load_pdf(filepath)
        return {"message": "PDF loaded succesfully",
                "filename":file.filename,"chunks":chunks}
    except Exception as e:
        raise HTTPException(500,f"Error loading PDF: {e}")
    finally:
        # This blocks runs NO MATTER WHAT, keeping your server hard drive clean
        if os.path.exists(filepath):
            os.remove(filepath)

@app.post("/load-text")
def load_text(request: TextRequest):
    try:
        chunks=engine.load_text(request.text,request.source_name)
        return {"message": "Text loaded","chunks":chunks}
    except Exception as e:
        raise HTTPException(500,str(e))
    
@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(400,"Question cannot be empty.")
    try:
        answer=engine.ask(request.question,request.n_results)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(500,str(e))
    
@app.get("/stats")
def get_stats():
    return engine.get_stats()

@app.delete("/reset")
def reset_collection():
    try:
        engine.reset() # Using the new method we built above
        return {"message": "Collection reset successfully"}
    except Exception as e:
        raise HTTPException(500, f"Reset failed: {str(e)}")
