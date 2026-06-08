import os
import datetime
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain.tools import tool


load_dotenv()


llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

search_tool=TavilySearch(
    max_results=3,
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

@tool
def get_date(dummy: str="")->str:
    """Returns today's date. Use this whenever you need to know the current date."""
    return datetime.datetime.now().strftime("%B %d, %Y")

@tool
def summarize_text(text: str)->str:
    """Summarize a long piece of text into 3 bullet points.
    Use this after retrieving search results to condense them."""
    lines=[l.strip() for l in text.split('\n') if l.strip()]
    key_points=lines[:3]
    return "\n".join(f". {p}" for p in key_points)

tools=[search_tool,get_date,summarize_text]


agent_executor=create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are an expert research assistant. "
        "Use the search tool to find facts, get_date for temporal context, "
        "and summarize_text to format final snippets cleanly."
    )
)

print("Research Agent ready. Type 'quit' to exit.\n")
while True:
    query=input("Research query: ").strip()
    if query.lower()=="quit":
        break
    if not query:
        continue
    print("\nAgent thinking...")
    try:
        result=agent_executor.invoke({"messages":[("user",query)]})
        print(f"\nFinal answer:\n{result['output']}\n")
    except ChatGoogleGenerativeAIError as e:
        if "429" in str(e):
            print("\n[System Notice] Google Free Tier servers are rate-limited right now.")
            print("Waiting 35 seconds to clear the rate-limit window... Please hold.")
            time.sleep(35)
            print("Resuming loop. Please re-enter your query.")
        else:
            print(f"\nAn error occurred: {e}")
        
    print("=" * 60)