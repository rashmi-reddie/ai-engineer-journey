import os
import asyncio
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv()

app=FastAPI(title="Real-time AI Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SYSTEM_PROMPT="""You are a helpful AI Engineering mentor.
Give Practical,concise answers. Use examples when helpful."""

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time AI Chat</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .chat-container {
            width: 100%;
            max-width: 600px;
            height: 80vh;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: #1a73e8;
            color: white;
            padding: 15px 20px;
            font-size: 1.2rem;
            font-weight: 600;
        }
        .messages-box {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            max-width: 75%;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.95rem;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .user {
            background-color: #e3f2fd;
            color: #0d47a1;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }
        .ai {
            background-color: #f1f3f4;
            color: #202124;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
        }
        .error {
            background-color: #ffebee;
            color: #c62828;
            align-self: center;
            text-align: center;
        }
        .input-area {
            display: flex;
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #e8eaed;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px;
            border: 1px solid #dadce0;
            border-radius: 6px;
            font-size: 1rem;
            outline: none;
        }
        input:focus {
            border-color: #1a73e8;
        }
        button {
            background: #1a73e8;
            color: white;
            border: none;
            padding: 0 20px;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #1557b0;
        }
        button:disabled {
            background: #dadce0;
            cursor: not-allowed;
        }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">AI Engineering Mentor</div>
    <div class="messages-box" id="messages"></div>
    <div class="input-area">
        <input type="text" id="messageText" placeholder="Ask a question..." autocomplete="off"/>
        <button id="sendBtn" onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
    // 1. Establish the persistent WebSocket connection to your FastAPI backend
    const ws = new WebSocket("ws://localhost:8003/ws");
    
    const messagesBox = document.getElementById('messages');
    const messageInput = document.getElementById('messageText');
    const sendButton = document.getElementById('sendBtn');
    let currentAiMessageElement = null;

    // Listen for incoming tokens from the server
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === "start") {
            // Create a brand new empty div for the upcoming AI stream
            currentAiMessageElement = document.createElement('div');
            currentAiMessageElement.className = 'message ai';
            currentAiMessageElement.innerText = 'Thinking...';
            messagesBox.appendChild(currentAiMessageElement);
            scrollToBottom();
        } 
        else if (data.type === "token") {
            // Remove the placeholder text on the first real token
            if (currentAiMessageElement.innerText === 'Thinking...') {
                currentAiMessageElement.innerText = '';
            }
            // Append the new character/token directly onto the screen instantly
            currentAiMessageElement.innerText += data.content;
            scrollToBottom();
        } 
        else if (data.type === "end") {
            // Lock finalized, clear tracking reference for the next cycle
            currentAiMessageElement = null;
            enableInput();
        } 
        else if (data.type === "error") {
            if (currentAiMessageElement) {
                currentAiMessageElement.innerText = "Error: " + data.content;
                currentAiMessageElement.className = 'message error';
            }
            enableInput();
        }
    };

    function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Display user message on screen immediately
        const userDiv = document.createElement('div');
        userDiv.className = 'message user';
        userDiv.innerText = text;
        messagesBox.appendChild(userDiv);
        
        // Send payload to backend over WebSocket
        ws.send(JSON.stringify({ message: text }));
        
        // Clean input field and temporarily disable it while streaming
        messageInput.value = '';
        disableInput();
        scrollToBottom();
    }

    function disableInput() {
        messageInput.disabled = true;
        sendButton.disabled = true;
    }

    function enableInput() {
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }

    function scrollToBottom() {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    // Allow user to press 'Enter' instead of clicking the button
    messageInput.addEventListener("keyup", function(event) {
        if (event.key === "Enter" && !messageInput.disabled) {
            sendMessage();
        }
    });
</script>

</body>
</html>
"""

    

    

    
llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
    streaming=True
)

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket]=[]
        
    async def connect(self,ws:WebSocket):
        await ws.accept()
        self.active.append(ws)
        
    def disconnect(self,ws:WebSocket):
        self.active.remove(ws)
        
manager=ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data=await ws.receive_json()
            user_msg=data.get("message","")
            if not user_msg.strip():
                continue
            await ws.send_json({"type":"start"})
            try:
                messages=[
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=user_msg)
                ]
                async for chunk in llm.astream(messages):
                    token=chunk.content
                    if token:
                        await ws.send_json({"type":"token","content":token})
                        await asyncio.sleep(0)
                await ws.send_json({"type":"end"})
            except Exception as e:
                await ws.send_json({"type":"error","content":str(e)})
    except WebSocketDisconnect:
        manager.disconnect(ws)