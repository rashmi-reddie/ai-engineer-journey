from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI(title="My First API",version="1.0")

class MessageRequest(BaseModel):
    text:str
    user_name: str="stranger"

@app.get("/")
def root():
    return {"message":"API is running", "status" : "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/echo")
def echo_message(request:MessageRequest):
    return {
        "you_said": request.text,
        "greeting": f"Hello {request.user_name}!",
        "length":len(request.text)
    }
    