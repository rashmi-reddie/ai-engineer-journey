import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from langchain_core.tools import tool

from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
import math,datetime

load_dotenv()

llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)


@tool
def calculator(expression: str)->str:
    """Evaluate a Python math expression safely."""
    try:
        return str(eval(expression,{"math":math,"__builtins__":{}}))
    except Exception as e:
        return f"Error: {e}"

@tool
def save_note(content: str)-> str:
    """Save an important note or fact to a local file for later reference
    Use this when the user asks to remember something"""
    with open("agent_notes.txt","a") as f:
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"[{timestamp}] {content}\n")
    return f"Note saved: {content}"

@tool
def read_notes(dummy: str="")->str:
    """Read all saved notes. Use this when user asks what was saved or remembered."""
    try:
        with open("agent_notes.txt","r") as f:
            notes=f.read()
        return notes if notes.strip() else "No notes saved yet."
    except FileNotFoundError:
        return "No notes file found yet."
    
@tool
def get_datetime(dummy: str="") -> str:
    """Get current date and time."""
    return datetime.datetime.now().strftime("%A, %B %d %Y at %H:%M")

search=TavilySearch(
    max_results=2,
    topic="general"
    # API key is auto-read from TAVILY_API_KEY env variable
)



tools=[calculator,save_note,read_notes,get_datetime,search]

#Create a Proper Structural Prompt Template
#Tool-calling agents require a slot for chat history and the agent_scratchpad

agent_executor=create_agent(
    model=llm,
    tools=tools,
    checkpointer=InMemorySaver(),
    system_prompt="You are a helpful personal assistant. Be concise and use tools when needed."
)

config = {"configurable": {"thread_id": "rashmitha_main"}}

print("Personal AI Assistant - with memory and tools")
print("Tools: calculator, web search, save notes, read notes, datetime")
print("Type 'quit' to exit.\n")

while True:
    user_input=input("You: ").strip()
    if user_input.lower()=="quit":
        break
    if not user_input:
        continue
    try:
        result = agent_executor.invoke({"messages":[{"role":"user","content":user_input}]},
                                config=config)
        print(f"Agent: {result['messages'][-1]}\n")
    except Exception as e:
        print(f"Agent Error encountered: {e}\n")