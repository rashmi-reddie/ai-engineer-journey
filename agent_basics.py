import os
import math
import time
import datetime
from dotenv import load_dotenv

# 1. Model Provider
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_ollama import ChatOllama
# 2. Modern Unified Agent Primitive (Replaces create_react_agent)
from langchain.agents import create_agent

# 3. Tool Engineering Abstractions
from langchain_core.tools import tool

load_dotenv()

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
   google_api_key=os.getenv("GEMINI_API_KEY"),
     temperature=0
 )
# llm = ChatOllama(
#     model="llama3.2",
#     temperature=0
# )
# --- Define Tools ---

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Input must be a valid Python math expression.
    Examples: '2+2', 'math.sqrt(16)', '15 * 24/3' """
    try:
        result = eval(expression, {"math": math, "__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"
    
@tool
def get_current_datetime(format: str = "%Y-%m-%d %H:%M") -> str:
    """Get the current date and time. Optionally specify format string."""
    return datetime.datetime.now().strftime(format)

@tool
def word_counter(text: str) -> str:
    """Count words, characters, and sentences in a given text."""
    words = len(text.split())
    chars = len(text)
    sentences = text.count('.') + text.count('!') + text.count('?')
    return (f"Words: {words}, Characters: {chars}, "
            f"Sentences: {sentences if sentences > 0 else 'unknown'}")
    
@tool
def unit_converter(query: str) -> str:
    """Convert between common units. Examples:
    '5 km to miles','100 celsius to fahrenheit', '10 kg to pounds'"""
    query = query.lower()
    try:
        if "km to miles" in query:
            num = float(query.split()[0])
            return f"{num} km = {num * 0.621371:.3f} miles"
        elif "miles to km" in query:
            num = float(query.split()[0])
            return f"{num} miles = {num * 1.60934:.3f} km"
        elif "celsius to fahrenheit" in query or "c to f" in query:
            num = float(query.split()[0])
            return f"{num}°C = {num * 9/5 + 32:.1f}°F"
        elif "fahrenheit to celsius" in query or "f to c" in query:
            num = float(query.split()[0])
            # FIXED: Corrected conversion logic for F to C
            return f"{num}°F = {(num - 32) * 5/9:.1f}°C" 
        elif "kg to pounds" in query or "kg to lbs" in query:
            num = float(query.split()[0])
            return f"{num} kg = {num * 2.20462:.2f} pounds"
        else:
            return "Unsupported conversion. Try: km to miles, celsius to fahrenheit, kg to pounds"
    except Exception as e:
        return f"Conversion error: {e}"

tools = [calculator, get_current_datetime, word_counter, unit_converter]

# --- Create the Modern Agent ---
# create_agent outputs a ready-to-run graph workflow.
# AgentExecutor and manual prompt hubs are no longer required.
agent_executor = create_agent(
    model=llm, 
    tools=tools,
    system_prompt="You are a helpful assistant with access to tools. Solve the user queries efficiently."
)

print("=== Modern LangChain Agent with 4 tools ===\n")

queries = [
    "What is the square root of 1764 multiplied by 3?",
    "What is today's date?",
    "Count the words in this text: FastAPI is a modern Python framework for building APIs quickly and efficiently.",
    "Convert 42 km to miles and also tell me what 37 celsius is in fahrenheit.",
]

for query in queries:
    print(f"\nQuery: {query}")
    print("-" * 50)
    
    try:
        # Execute agent workflow
        result = agent_executor.invoke({"messages": [("user", query)]})
        print(f"Final answer: {result['messages'][-1].content}\n")
    except Exception as e:
        print(f"Error executing query: {e}")
        print("Skipping to next query due to error...")
    
    # Increased cooldown window to clear out Free Tier RPM caps
    print("Pausing to clear rate limits...")
    time.sleep(12)