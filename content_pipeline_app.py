import os
import time
import streamlit as st
from typing import TypedDict, Annotated,Literal
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage,AIMessage
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

st.set_page_config(page_title="Multi-Agent Content Pipeline",layout="wide")
st.title("Multi-Agent Content Pipeline")
st.caption("Researcher -> Writer -> Reviewer working together")

@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
    )
    
@st.cache_resource
def get_search():
    return TavilySearch(max_results=3,topic="general")

def safe_invoke(llm, messages, retries=3):
    """Safely calls the LLM with exponential backoff on 429 Rate Limits."""
    for attempt in range(retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 30 * (attempt + 1)
                st.warning(f"Rate limited. Waiting {wait}s before retry {attempt+1}/{retries}...")
                time.sleep(wait)
            else:
                raise e
    raise RuntimeError("Max retries reached. Try again later.")

@st.cache_resource
def build_graph():
    llm=get_llm()
    search=get_search()
    
    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage],add_messages]
        task: str
        research: str
        draft: str
        review: str
        next_step:str
        iteration:int
        
    def researcher_node(state: AgentState)->dict:
        task=state["task"]
        try:
            results=search.invoke({"query": task})
            if isinstance(results,list):
                facts="\n".join([
                    f" - {r.get('content',str(r))[:200]}" for r in results[:3]
                ])
            else:
                facts=str(results)[:600]
        except Exception:
            facts="Using general knowledge."
        
        response=safe_invoke(llm,[HumanMessage(content=f"""You are a researcher.
                                Task: {task}
                                Facts found : {facts}
            Summarize in 4-5 key bullet points.""")])
        return{
            "messages": [AIMessage(content=f"[Researcher]: {response.content}")],
            "research":response.content,
            "next_step":"writer"
        }
        
    def writer_node(state: AgentState) -> dict:
        response=safe_invoke(llm,[HumanMessage(content=f"""You are a professional writer.
                    Task: {state['task']}
                    Research: {state['research']}
        Write a clear 3-paragraph response for a technical audience.""")])
        
        return{
            "messages":[AIMessage(content=f"[Writer]: {response.content}")],
            "draft":response.content,
            "next_step":"reviewer"
        }
    
    def reviewer_node(state: AgentState) -> dict:
        response=safe_invoke(llm,HumanMessage(content=f"""You are a quality reviewer.
                                    Task: {state['task']}
                                    Draft: {state['draft']}
                    Reply ONLY with:
                    APPROVED: [reason] if draft accurate and complete
                    REVISION_NEEDED: [specific issues] - if draft needs work"""))
        review =response.content
        iteration=state.get("iteration",0)+1
        next_step="done" if ("APPROVED" in review or iteration >= 2) else "writer"
        return{
            "messages": [AIMessage(content=f"[Reviewer]: {review}")],
            "review": review,
            "next_step": next_step,
            "iteration": iteration
        }
    def route(state: AgentState)->Literal["writer","__end__"]:
        return "writer" if state.get("next_step")=="writer" else END
    
    g=StateGraph(AgentState)
    g.add_node("researcher",researcher_node)
    g.add_node("writer",writer_node)
    g.add_node("reviewer",reviewer_node)
    g.set_entry_point("researcher")
    g.add_edge("researcher","writer")
    g.add_edge("writer","reviewer")
    g.add_conditional_edges("reviewer",route,{"writer":"writer",END:END})
    return g.compile(checkpointer=InMemorySaver())

app=build_graph()
task=st.text_input(
    "Enter your research task",
    placeholder="e.g. What are the best AI engineering skills to learn in 2026?"
)
if st.button("Run Pipeline",type="primary"):
    if not task.strip():
        st.error("Please enter a task.")
    else:
        col1,col2,col3=st.columns(3)
        r_box=col1.empty()
        w_box=col2.empty()
        rv_box=col3.empty()
        r_box.info("Researcher: waiting...")
        w_box.info("Writer: waiting...")
        rv_box.info("Reviewer: waiting...")
        
        import uuid
        config={"configurable":{"thread_id": str(uuid.uuid4())}}
        
        with st.spinner("Agents working..."):
            result=app.invoke({
                "messages":[HumanMessage(content=task)],
                "task":task,
                "research":"",
                "draft":"",
                "review":"",
                "next_step":"researcher",
                "iteration":0
            },config=config)
        
        r_box.success("Researcher done")
        st.expander("Researcher findings").write(result.get("research",""))
        
        w_box.success("Writer done")
        st.expander("Draft (iteration {})".format(
            result.get("iteration",1)
        )).write(result.get("draft",""))
        
        verdict=result.get("review","")
        if "APPROVED" in verdict:
            rv_box.success("Reviewer: APPROVED")
        else:
            rv_box.warning("Reviewer: revision was needed")
        st.expander("Review verdict").write(verdict)
        
        st.divider()
        st.subheader("Final output")
        st.write(result.get("draft",""))
