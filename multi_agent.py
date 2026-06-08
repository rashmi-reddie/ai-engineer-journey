import os
from typing import TypedDict , Annotated, Literal
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)

search=TavilySearch(
    max_results=3,
    topic="general"
)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]
    task: str
    research: str
    draft:str
    review: str
    max_step:str
    iteration:int
    
def researcher_node(state: AgentState)->dict:
    print(" [Researcher] searching for information...")
    task=state["task"]
    try:
        search_results=search.invoke({"query":task})
        if isinstance(search_results,list):
            research="\n".join([
                f"- {r.get('content',r.get('snippet',str(r)))[:200]} for r in search_results[:3]"
            ])
        else:
            research=str(search_results)[:600]
    except Exception as e:
        research=f"Search unavailable: {e}. Using general knowledge."
    
    summary_prompt=f"""You are a research assistant.
    Task: {task}
    Search results: {research}
    
    Summarize the key facts in 3-5 bullet points. Be specific and factual."""
    response=llm.invoke([HumanMessage(content=summary_prompt)])
    research_output=response.content
    return{
        "messages":[AIMessage(content=f"[Researcher]: {research_output}")],
        "research":research_output,
        "next_step":"writer"
    }

def writer_node(state: AgentState)->dict:
    print(" [Writer] drafting content...")
    write_prompt=f"""You are a professional writer.
    Task: {state['task']}
    Research Provided: {state['research']}
    
    Write a clear, well-structured response of 3-4 paragraphs.
    Use the research to support your points.
    Write for a technical audience"""
    
    response=llm.invoke([HumanMessage(content=write_prompt)])
    draft=response.content
    
    return{
        "messages":[AIMessage(content=f"[Writer]: {draft}")],
        "draft":draft,
        "next_step":"reviewer"
    }
    
def reviewer_node(state: AgentState)->dict:
    print(" [Reviewer] checking quality...")
    review_prompt=f"""You are a strict quality reviewer.
    Original task:{state['task']}
    Draft to review: {state['draft']}
    
    Review this draft and respond with only one of these two formats:
    
    If the draft is good (accurate,clear,complete):
    APPROVED: [one sentence explaining why it's good]
    
    If the draft needs work:
    REVISION_NEEDED:
    [specific list of what needs to change]
    
    Be strict - only approve if genuinely good."""
    
    response=llm.invoke([Humanmessage(content=review_prompt)])
    review=response.content
    iteration=state.get("iteration",0)+a1
    
    if "APPROVED" in review or iteration>=2:
        next_step="done"
    else:
        next_step="writer"
        
    return{
        "messages":[AIMessage(content=f"[Reviewer]: {review}")],
        "review":review,
        "next_step":next_step,
        "iteration":iteration
    }
    
def supervisor_router(state: AgentState)-> Literal["researcher","writer","reviewer","__end__"]:
    next_step=state.get("next_step","researcher")
    print(f" [Supervisor] roting to: {next_step}")
    if next_step=="done":
        return END
    return next_step

graph=StateGraph(AgentState)
graph.add_node("researcher",researcher_node)
graph.add_node("writer",writer_node)
graph.add_node("reviewer",reviewer_node)

graph.set_entry_point("researcher")
graph.add_edge("researcher","writer")
graph.add_edge("writer","reviewer")
graph.add_conditional_edges(
    "reviewer",
    supervisor_router,
    {
        "writer":"writer",
        END:END
    }
)
checkpointer=InMemorySaver()
app=graph.compile(checkpointer=checkpointer)

def run_multi_agent(task: str,thread_id: str="session_1"):
    print(f"\nTask: {task}")
    print("=" * 60)
    config={"configurable":{"thread_id":thread_id}}
    result=app.invoke({
        "messages":[HumanMessage(content=task)],
        "task":task,
        "research":"",
        "draft":"",
        "review":"",
        "next_step":"researcher",
        "iteration":0
    },config=config)
    
    print("\nFinal draft:")
    print("-" * 40)
    print(result["draft"])
    print("\nReview verdict:")
    print(result["review"])
    return result

if __name__=="__main__":
    run_multi_agent(
        "What are the most in-demand AI engineering skills for freshers in India in 2026?"
    )