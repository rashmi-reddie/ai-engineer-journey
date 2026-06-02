import os
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path="../.env")

app=FastAPI(title="AI Chat API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

sessions={}

class ChatRequest(BaseModel):
    session_id : str
    message:str
    system_prompt: str ="You are a helpful AI Assistant. Be concise and clear."
    
class ChatResponse(BaseModel):
    session_id:str
    reply:str
    turn_count:int

@app.get("/")
def root():
    return {"message": "AI Chat API is running", "status":"ok"}

@app.get("/sessions")
def list_sessions():
    return{
        "active_sessions": list(sessions.keys()),
        "count": len(sessions)
        
    }
    
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if request.session_id not in sessions:
            sessions[request.session_id]=[]
            
        history=sessions[request.session_id]
        history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=request.message)]
            )
        )
        
        config=types.GenerateContentConfig(
            system_instruction=request.system_prompt
        )
        
        response=client.models.generate_content(
            model="gemini-2.5-flash",
            config=config,
            contents=history
        )
        
        reply=response.text
        history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=reply)]
            )
        )
        return ChatResponse(
            session_id=request.session_id,
            reply=reply,
            turn_count=len(history)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.delete("/sessions/{session_id}")
def clear_session(session_id:str):
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")